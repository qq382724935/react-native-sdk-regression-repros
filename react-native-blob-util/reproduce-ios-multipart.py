#!/usr/bin/env python3
"""Execute the SDK's unchanged Objective-C multipart builder on macOS."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


HEAD = r'''
#import <Foundation/Foundation.h>
#define RCTLogWarn(...) ((void)0)
static NSString *FILE_PREFIX = @"ReactNativeBlobUtil-file://";

@interface ReactNativeBlobUtilFS : NSObject
+ (NSString *)getPathOfAsset:(NSString *)path;
+ (void)readFile:(NSString *)path
        encoding:(NSString *)encoding
        transformFile:(BOOL)transform
        onComplete:(void (^)(NSData *, NSString *, NSString *))callback;
@end

@implementation ReactNativeBlobUtilFS
+ (NSString *)getPathOfAsset:(NSString *)path { return path; }
+ (void)readFile:(NSString *)path
        encoding:(NSString *)encoding
        transformFile:(BOOL)transform
        onComplete:(void (^)(NSData *, NSString *, NSString *))callback {
    if ([path isEqualToString:@"nil-content"]) {
        callback(nil, nil, nil);
    } else if ([path isEqualToString:@"explicit-error"]) {
        callback(nil, @"EIO", @"Controlled read failure");
    } else if ([path isEqualToString:@"empty-file"]) {
        callback([NSData data], nil, nil);
    } else {
        callback([@"payload" dataUsingEncoding:NSUTF8StringEncoding], nil, nil);
    }
}
@end

@interface FormBuilder : NSObject
+ (void)buildFormBody:(NSArray *)form
        boundary:(NSString *)boundary
        onComplete:(void (^)(NSData *, BOOL))onComplete;
@end

@implementation FormBuilder
'''

TAIL = r'''
@end

int main(void) {
    @autoreleasepool {
        int failures = 0;
        for (NSString *name in @[@"nil-content", @"explicit-error", @"empty-file", @"nonempty-file"]) {
            __block int callbacks = 0;
            __block BOOL error = NO;
            __block NSData *body = nil;
            NSArray *form = @[@{
                @"name": @"file",
                @"filename": @"fixture.txt",
                @"data": [FILE_PREFIX stringByAppendingString:name]
            }];
            [FormBuilder buildFormBody:form boundary:@"fixture" onComplete:^(NSData *data, BOOL failed) {
                callbacks++;
                error = failed;
                body = data;
            }];
            BOOL expectedError = [name isEqualToString:@"nil-content"] || [name isEqualToString:@"explicit-error"];
            BOOL passed = callbacks == 1 && error == expectedError;
            if (!expectedError) {
                NSString *text = [[NSString alloc] initWithData:body encoding:NSUTF8StringEncoding];
                // The outer request builder adds the final boundary; this method returns parts.
                NSString *ending = [name isEqualToString:@"empty-file"]
                    ? @"\r\n\r\n\r\n"
                    : @"\r\n\r\npayload\r\n";
                passed = passed && [text containsString:@"filename=\"fixture.txt\""] && [text hasSuffix:ending];
            }
            printf("%s: %s (callbacks=%d, error=%s, expected_error=%s)\n",
                   name.UTF8String, passed ? "PASS" : "FAIL", callbacks,
                   error ? "true" : "false", expectedError ? "true" : "false");
            if (!passed) failures++;
        }
        printf("4 cases; %d failure(s)\n", failures);
        return failures == 0 ? 0 : 1;
    }
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', required=True, type=Path, help='Extracted react-native-blob-util package root')
    args = parser.parse_args()
    if sys.platform != 'darwin':
        parser.error('This reproduction requires macOS, Foundation and clang++.')

    metadata = json.loads((args.sdk / 'package.json').read_text())
    if metadata.get('name') != 'react-native-blob-util':
        parser.error('--sdk must point to a react-native-blob-util package root')

    source = (args.sdk / 'ios/ReactNativeBlobUtilReqBuilder.mm').read_bytes()
    start_marker = b'+(void) buildFormBody:'
    end_marker = b'\n+(NSString *) getHeaderIgnoreCases:'
    if source.count(start_marker) != 1 or source.count(end_marker) != 1:
        parser.error('SDK method boundaries changed; inspect the source before adapting this reproduction.')
    start = source.index(start_marker)
    end = source.index(end_marker, start)
    method = source[start:end]
    print('SDK version:', metadata['version'], flush=True)
    print('Builder source SHA-256:', hashlib.sha256(source).hexdigest(), flush=True)
    print('Extracted method SHA-256:', hashlib.sha256(method).hexdigest(), flush=True)

    with tempfile.TemporaryDirectory(prefix='rnblob-multipart-') as directory:
        output = Path(directory)
        # Preserve the extracted method bytes; only its filesystem boundary is controlled.
        (output / 'Form.mm').write_bytes(HEAD.encode() + method + TAIL.encode())
        compilation = subprocess.run([
            'clang++', '-fobjc-arc', '-fblocks', '-framework', 'Foundation',
            'Form.mm', '-o', 'reproduce',
        ], cwd=output)
        if compilation.returncode:
            return compilation.returncode
        return subprocess.run(['./reproduce'], cwd=output).returncode


if __name__ == '__main__':
    sys.exit(main())

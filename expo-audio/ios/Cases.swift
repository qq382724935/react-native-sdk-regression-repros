func check(_ value: Bool, _ message: String) {
  if !value { print("FAIL: " + message); exit(1) }
}
let scenario = CommandLine.arguments.last!
if scenario == "startup-cleanup" {
  AVAudioEngine.startThrows = true
  AVAudioEngine.hardware = AVAudioFormat(commonFormat: .pcmFormatFloat32, sampleRate: 48000, channels: 1, interleaved: true)!
  let stream = AudioStream(options: AudioStreamOptions(sampleRate: 48000, channels: 1, encoding: .float32))
  var failed = false
  do { try stream.start() } catch { failed = true }
  check(failed, "controlled engine start must throw")
  try? stream.stop()
  let engine = AVAudioEngine.latest!
  let cleaned = engine.inputNode.tap == nil && engine.stops > 0
  print("startup-cleanup: tapInstalled=\(engine.inputNode.tap != nil), stops=\(engine.stops), sessionActive=\(AVAudioSession.instance.active)")
  check(cleaned, "stop after failed startup must clean up the stream's installed tap and engine")
} else if scenario == "stereo-layout" {
  let format = AVAudioEngine.hardware
  let stream = AudioStream(options: AudioStreamOptions(sampleRate: 48000, channels: 2, encoding: .float32))
  try stream.start()
  let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: 4)!
  buffer.frameLength = 2
  // Extra valid allocation makes the bad copy deterministic without reading out of bounds.
  let left = buffer.floatChannelData![0], right = buffer.floatChannelData![1]
  left[0] = 1; left[1] = 2; left[2] = 99; left[3] = 99
  right[0] = 3; right[1] = 4; right[2] = 99; right[3] = 99
  AVAudioEngine.latest!.inputNode.tap!(buffer, AVAudioTime(hostTime: 0))
  let payload = stream.events.last { $0.0 == "audioStreamBuffer" }!.1
  let bytes = (payload["data"] as! ArrayBuffer).data
  let samples = bytes.withUnsafeBytes { Array($0.bindMemory(to: Float.self)) }
  print("stereo-layout: actual=\(samples), expected=[1, 3, 2, 4]")
  check(samples == [1, 3, 2, 4], "stereo samples must be interleaved")
  try? stream.stop()
} else if scenario == "converter-failure" {
  forceConverterUnavailable = true
  AVAudioEngine.hardware = AVAudioFormat(commonFormat: .pcmFormatFloat32, sampleRate: 48000, channels: 1, interleaved: true)!
  let stream = AudioStream(options: AudioStreamOptions(sampleRate: 16000, channels: 1, encoding: .int16))
  var failed = false
  do { try stream.start() } catch { failed = true }
  if !failed {
    let input = AVAudioPCMBuffer(pcmFormat: AVAudioEngine.hardware, frameCapacity: 2)!
    input.frameLength = 2
    input.floatChannelData![0][0] = 0.5; input.floatChannelData![0][1] = -0.5
    AVAudioEngine.latest!.inputNode.tap!(input, AVAudioTime(hostTime: 0))
    let payload = stream.events.last { $0.0 == "audioStreamBuffer" }!.1
    let data = (payload["data"] as! ArrayBuffer).data
    check(data.count == 8 && payload["encoding"] == nil, "expected undisclosed float fallback")
    print("converter-failure: startSucceeded=true, requested=int16, emitted=float32, encodingField=missing")
    try? stream.stop()
  } else {
    print("converter-failure: startRejected=true")
  }
  check(failed, "unavailable conversion must not silently change the requested PCM encoding")
} else {
  fatalError("unknown scenario")
}

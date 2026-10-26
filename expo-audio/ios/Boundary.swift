import Foundation
import AVFoundation

// Real AVAudioFormat, AVAudioPCMBuffer and AVAudioConverter; controlled engine/session/Expo boundaries.
enum AudioStreamEncoding: String { case int16, float32 }
struct AudioStreamOptions { var sampleRate: Double; var channels: Int; var encoding: AudioStreamEncoding }
class GenericException<T>: Error {
  let param: T
  init(_ param: T) { self.param = param }
  var code: String { "" }
  var reason: String { "" }
}
class SharedObject {
  var events: [(String, [String: Any])] = []
  func emit(event: String, payload: [String: Any]) { events.append((event, payload)) }
  func sharedObjectWillRelease() {}
}
class ArrayBuffer {
  let data: Data
  init(_ data: Data) { self.data = data }
  static func copy<T>(of pointer: UnsafePointer<T>, count: Int) -> ArrayBuffer {
    ArrayBuffer(Data(bytes: pointer, count: count))
  }
}
enum AudioStreamFileFormat { case wav }
struct AudioStreamFileException: Error {
  let message: String
  init(_ message: String) { self.message = message }
}
struct AudioStreamFileRecordingResult {
  let uri: String
  let duration: Double
  let size: Int
  let sampleRate: Int
  let channels: Int
  let encoding: AudioStreamEncoding
}
class AudioStreamFileWriter {
  let url: URL
  init(url: URL, format: AudioStreamFileFormat, sampleRate: Double, channels: Int, encoding: AudioStreamEncoding) throws {
    self.url = url
  }
  func append(pcmData: Data) throws {}
  func finish() throws -> (Int64, Int64) { (0, 0) }
}
let AVAudioSessionInterruptionTypeKey = "type"
class AVAudioSession: NSObject {
  enum Category { case record }
  enum Mode { case measurement }
  enum Options { case notifyOthersOnDeactivation }
  enum InterruptionType: UInt { case began = 1, ended = 0 }
  static let interruptionNotification = Notification.Name("controlled.interruption")
  static let mediaServicesWereLostNotification = Notification.Name("controlled.mediaLost")
  static let instance = AVAudioSession()
  static func sharedInstance() -> AVAudioSession { instance }
  var active = false
  func setCategory(_ category: Category, mode: Mode) throws {}
  func setPreferredSampleRate(_ value: Double) throws {}
  func setActive(_ value: Bool, options: Options? = nil) throws { active = value }
}
class AVAudioInputNode {
  var tap: ((AVAudioPCMBuffer, AVAudioTime) -> Void)?
  var removals = 0
  func outputFormat(forBus: Int) -> AVAudioFormat { AVAudioEngine.hardware }
  func installTap(onBus: Int, bufferSize: AVAudioFrameCount, format: AVAudioFormat,
                  block: @escaping (AVAudioPCMBuffer, AVAudioTime) -> Void) { tap = block }
  func removeTap(onBus: Int) { removals += 1; tap = nil }
}
class AVAudioEngine: NSObject {
  static var latest: AVAudioEngine?
  static var hardware = AVAudioFormat(commonFormat: .pcmFormatFloat32, sampleRate: 48000, channels: 2, interleaved: false)!
  static var startThrows = false
  let inputNode = AVAudioInputNode()
  var stops = 0
  override init() { super.init(); Self.latest = self }
  func start() throws {
    if Self.startThrows { throw NSError(domain: "ControlledEngineStart", code: 1) }
  }
  func stop() { stops += 1 }
}
var forceConverterUnavailable = false
func makeConverter(from: AVAudioFormat, to: AVAudioFormat) -> AVAudioConverter? {
  forceConverterUnavailable ? nil : AVAudioConverter(from: from, to: to)
}

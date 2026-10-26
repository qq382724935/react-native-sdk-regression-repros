package android.media

import java.nio.ByteBuffer
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.Executor
import java.util.concurrent.atomic.AtomicInteger

object AudioFormat {
  const val CHANNEL_IN_STEREO = 12
  const val CHANNEL_IN_MONO = 16
  const val ENCODING_PCM_16BIT = 2
  const val ENCODING_PCM_FLOAT = 4
}
object MediaRecorder { object AudioSource { const val MIC = 1 } }
open class AudioManager {
  open class AudioRecordingCallback {
    open fun onRecordingConfigChanged(configs: MutableList<AudioRecordingConfiguration>) {}
  }
}
class AudioRecordingConfiguration(val clientAudioSessionId: Int, val isClientSilenced: Boolean)

enum class ReadBehavior { ZERO, DEAD_OBJECT, ONE_FRAME }

// Only the Android hardware boundary is controlled; the SDK capture coroutine is real.
class AudioRecord(source: Int, val sampleRate: Int, channelConfig: Int, val audioFormat: Int, size: Int) {
  companion object {
    const val STATE_INITIALIZED = 1
    const val RECORDSTATE_RECORDING = 3
    const val READ_BLOCKING = 0
    const val READ_NON_BLOCKING = 1
    const val ERROR = -1
    const val ERROR_BAD_VALUE = -2
    const val ERROR_DEAD_OBJECT = -6
    val behaviors = ConcurrentLinkedQueue<ReadBehavior>()
    @Volatile var latest: AudioRecord? = null
    fun getMinBufferSize(rate: Int, channels: Int, format: Int): Int = 320
  }
  private val behavior = behaviors.poll() ?: ReadBehavior.ZERO
  val channelCount = if (channelConfig == AudioFormat.CHANNEL_IN_STEREO) 2 else 1
  val state = STATE_INITIALIZED
  val audioSessionId = 1
  @Volatile var recordingState = 0
  @Volatile var stopThrows = false
  val readCount = AtomicInteger()
  val stopCount = AtomicInteger()
  val releaseCount = AtomicInteger()
  init { latest = this }
  fun startRecording() { recordingState = RECORDSTATE_RECORDING }
  fun stop() {
    stopCount.incrementAndGet()
    if (stopThrows) throw IllegalStateException("controlled AudioRecord.stop failure")
    recordingState = 0
  }
  fun release() { releaseCount.incrementAndGet(); recordingState = 0 }
  fun registerAudioRecordingCallback(executor: Executor, callback: AudioManager.AudioRecordingCallback) {}
  fun unregisterAudioRecordingCallback(callback: AudioManager.AudioRecordingCallback) {}
  fun read(buffer: ByteBuffer, size: Int, mode: Int): Int {
    val count = readCount.incrementAndGet()
    // Throttle the invalid-object boundary to avoid a runaway test allocating direct buffers.
    Thread.sleep(2)
    return when (behavior) {
      ReadBehavior.DEAD_OBJECT -> ERROR_DEAD_OBJECT
      ReadBehavior.ONE_FRAME -> if (count == 1) {
        // AudioRecord writes at index zero and leaves ByteBuffer.position() unchanged.
        repeat(4) { buffer.put(it, 0x2a.toByte()) }
        4
      } else 0
      ReadBehavior.ZERO -> 0
    }
  }
}

package androidx.media3.common.audio
import java.nio.ByteBuffer

class AudioProcessor {
  data class AudioFormat(val sampleRate: Int, val channelCount: Int, val encoding: Int)
  class StreamMetadata { companion object { val DEFAULT = StreamMetadata() } }
}
// The selected format equals the requested format; resampling is outside these scenarios.
class SonicAudioProcessor {
  fun setOutputSampleRateHz(rate: Int): Unit = error("Resampling is outside this reproduction")
  fun configure(format: AudioProcessor.AudioFormat): AudioProcessor.AudioFormat = error("Unexpected resampling")
  fun flush(metadata: AudioProcessor.StreamMetadata): Unit = error("Unexpected resampling")
  fun queueInput(buffer: ByteBuffer): Unit = error("Unexpected resampling")
  fun getOutput(): ByteBuffer = error("Unexpected resampling")
  fun reset(): Unit = error("Unexpected resampling")
}

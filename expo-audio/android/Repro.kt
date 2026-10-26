package repro

import android.media.AudioRecord
import android.media.ReadBehavior
import expo.modules.audio.AudioStream
import expo.modules.audio.AudioStreamEncoding
import expo.modules.audio.AudioStreamOptions
import expo.modules.kotlin.AppContext
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.SupervisorJob
import java.util.concurrent.ConcurrentLinkedQueue
import kotlin.coroutines.CoroutineContext
import kotlin.system.exitProcess

class QueuedDispatcher : CoroutineDispatcher() {
  private val queue = ConcurrentLinkedQueue<Runnable>()
  override fun dispatch(context: CoroutineContext, block: Runnable) { queue.add(block) }
  fun size() = queue.size
  fun drain() { while (true) (queue.poll() ?: return).run() }
}

private fun waitUntil(description: String, predicate: () -> Boolean) {
  val deadline = System.nanoTime() + 3_000_000_000L
  while (!predicate()) {
    check(System.nanoTime() < deadline) { "Timed out waiting for $description" }
    Thread.sleep(1)
  }
}

private fun newStream(behavior: ReadBehavior = ReadBehavior.ZERO): Pair<AudioStream, QueuedDispatcher> {
  AudioRecord.behaviors.clear()
  AudioRecord.behaviors.add(behavior)
  val dispatcher = QueuedDispatcher()
  return AudioStream(AppContext(CoroutineScope(SupervisorJob() + dispatcher)), AudioStreamOptions().apply {
    sampleRate = 16000
    channels = 1
    encoding = AudioStreamEncoding.INT16
  }) to dispatcher
}

private fun stopException(): Boolean {
  val (stream, queue) = newStream()
  stream.start()
  val recorder = AudioRecord.latest!!
  recorder.stopThrows = true
  val firstError = runCatching { stream.stop() }.exceptionOrNull()
  runCatching { stream.stop() }
  runCatching { stream.sharedObjectDidRelease() }
  queue.drain()
  val passed = firstError != null && recorder.releaseCount.get() == 1
  println("stop_exception: releaseCount=${recorder.releaseCount.get()}, stopCount=${recorder.stopCount.get()}, isStreaming=${stream.isStreaming}, expected releaseCount=1, passed=$passed")
  return passed
}

private fun deadObject(): Boolean {
  val (stream, queue) = newStream(ReadBehavior.DEAD_OBJECT)
  stream.start()
  val recorder = AudioRecord.latest!!
  waitUntil("fatal read to terminate or be retried ten times") {
    recorder.releaseCount.get() > 0 || recorder.readCount.get() >= 10
  }
  val reads = recorder.readCount.get()
  val active = stream.isStreaming
  val releases = recorder.releaseCount.get()
  queue.drain()
  val statuses = stream.events.filter { it.first == "audioStreamStatus" }.map { it.second["isStreaming"] }
  val recreated = AudioRecord.latest !== recorder
  val passed = reads == 1 && releases == 1 && (!active || recreated)
  runCatching { stream.stop() }
  println("dead_object: reads=$reads, isStreaming=$active, releaseCount=$releases, statuses=$statuses, expected no retry of the invalid recorder and inactive state, passed=$passed")
  return passed
}

private fun statusSnapshots(): Boolean {
  val (stream, queue) = newStream()
  stream.start()
  stream.stop()
  queue.drain()
  val statuses = stream.events.filter { it.first == "audioStreamStatus" }.map { it.second["isStreaming"] }
  val passed = statuses == listOf(true, false)
  println("status_snapshot: statuses=$statuses, expected=[true, false], passed=$passed")
  return passed
}

private fun staleBuffer(): Boolean {
  val (stream, queue) = newStream(ReadBehavior.ONE_FRAME)
  stream.start()
  waitUntil("the first status and one PCM delivery to queue") { queue.size() >= 2 }
  stream.stop()
  stream.start()
  queue.drain()
  val staleFrames = stream.events.count { it.first == "audioStreamBuffer" }
  val statuses = stream.events.filter { it.first == "audioStreamStatus" }.map { it.second["isStreaming"] }
  val passed = staleFrames == 0
  stream.stop()
  println("stale_buffer: oldFramesDeliveredAfterRestart=$staleFrames, statuses=$statuses, expected oldFramesDeliveredAfterRestart=0, passed=$passed")
  return passed
}

fun main(args: Array<String>) {
  val scenarios = linkedMapOf("stop_exception" to ::stopException, "dead_object" to ::deadObject,
    "status_snapshot" to ::statusSnapshots, "stale_buffer" to ::staleBuffer)
  val selected = args.singleOrNull() ?: "all"
  require(selected == "all" || scenarios.containsKey(selected)) { "Unknown scenario: $selected" }
  var failures = 0
  scenarios.filterKeys { selected == "all" || it == selected }.forEach { (name, test) ->
    try { if (!test()) failures++ } catch (error: Throwable) {
      failures++
      System.err.println("$name: harness error: $error")
      error.printStackTrace()
    }
  }
  println("SUMMARY failures=$failures")
  exitProcess(if (failures == 0) 0 else 1)
}

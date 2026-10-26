package expo.modules.kotlin.sharedobjects
import expo.modules.kotlin.AppContext
import java.util.Collections
open class SharedObject(val appContext: AppContext?) {
  val events = Collections.synchronizedList(mutableListOf<Pair<String, Map<String, Any>>>())
  fun emit(name: String, payload: Map<String, Any>) { events.add(name to payload.toMap()) }
  open fun sharedObjectDidRelease() {}
}

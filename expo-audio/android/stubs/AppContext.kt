package expo.modules.kotlin
import kotlinx.coroutines.CoroutineScope
class AppContext(val mainQueue: CoroutineScope) { val jsLogger = Logger() }
class Logger { fun warn(message: String, error: Exception) {} }

package expo.modules.kotlin.exception
open class CodedException(val code: String?, message: String?, cause: Throwable?) : Exception(message, cause) {
  constructor(message: String) : this(null, message, null)
}

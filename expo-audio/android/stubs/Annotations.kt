package androidx.annotation
import kotlin.reflect.KClass
annotation class RequiresPermission(val value: String)
annotation class OptIn(vararg val markerClass: KClass<*>)

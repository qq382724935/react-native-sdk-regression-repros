fun moveCamera(position: Map<String, Any>, duration: Int) {
    mainHandler.post {
    val current = aMap.cameraPosition
    val builder = CameraPosition.Builder(current)
    if (position.containsKey("target") && position["target"] != null) {
      val target = position["target"] as? Map<*, *>
        ?: throw IllegalArgumentException("Invalid camera target")
      val lat = (target["latitude"] as? Number)?.toDouble()
      val lng = (target["longitude"] as? Number)?.toDouble()
      require(lat != null && lng != null && lat.isFinite() && lng.isFinite() &&
        lat in -90.0..90.0 && lng in -180.0..180.0) { "Invalid camera target" }
      builder.target(LatLng(lat, lng))
    }
    fun number(key: String): Float? {
      val value = position[key] ?: return null
      val number = (value as? Number)?.toFloat()
      require(number != null && number.isFinite()) { "Invalid camera $key" }
      return number
    }
    number("zoom")?.let { builder.zoom(it.coerceIn(3f, 20f)) }
    number("tilt")?.let { builder.tilt(it.coerceIn(0f, 60f)) }
    number("bearing")?.let { builder.bearing(it) }
    val update = CameraUpdateFactory.newCameraPosition(builder.build())
    if (duration > 0) aMap.animateCamera(update, duration.toLong(), null)
    else aMap.moveCamera(update)
      }
  }

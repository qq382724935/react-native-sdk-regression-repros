fun getCurrentLocation(promise: Promise) {
        val settled = AtomicBoolean(false)
        var tempClient: AMapLocationClient? = null

        fun finish(location: AMapLocation?, error: Exception? = null) {
            if (!settled.compareAndSet(false, true)) return
            val client = tempClient
            tempClient = null
            if (client != null) {
                // Cleanup may reenter the listener or throw; neither can settle again.
                runCatching { client.stopLocation() }
                runCatching { client.onDestroy() }
            }
            if (error != null) {
                promise.reject("LOCATION_ERROR", "定位失败", error)
            } else if (location != null && location.errorCode == 0) {
                try {
                    promise.resolve(formatLocation(location))
                } catch (exception: Exception) {
                    promise.reject("LOCATION_ERROR", "定位结果不可用", exception)
                }
            } else {
                promise.reject("LOCATION_ERROR", location?.errorInfo ?: "定位失败", null)
            }
        }

        try {
            val onceOption = AMapLocationClientOption().apply {
                isOnceLocation = true
                locationOption?.let { opt ->
                    locationMode = opt.locationMode
                    httpTimeOut = opt.httpTimeOut
                    geoLanguage = opt.geoLanguage
                }
                isNeedAddress = locationOption?.isNeedAddress ?: true
                setMockEnable(mockEnable)
            }
            val client = AMapLocationClient(appContext)
            tempClient = client
            client.setLocationOption(onceOption)
            client.setLocationListener { location -> finish(location) }
            if (!settled.get()) client.startLocation()
        } catch (exception: Exception) {
            finish(null, exception)
        }
    }

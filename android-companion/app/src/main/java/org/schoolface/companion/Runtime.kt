package org.schoolface.companion

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.preferencesDataStore
import java.time.Instant
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

enum class WatchStatus { Unsupported }
interface WatchTransport {
    fun connect(): WatchStatus
    fun sendState(state: ScheduleState): WatchStatus
    fun disconnect()
    fun getStatus(): WatchStatus
}

object NoOpWatchTransport : WatchTransport {
    override fun connect() = WatchStatus.Unsupported
    override fun sendState(state: ScheduleState) = WatchStatus.Unsupported
    override fun disconnect() = Unit
    override fun getStatus() = WatchStatus.Unsupported
}

private val Context.settings by preferencesDataStore("schoolface_settings")

object ScheduleRuntime {
    private val enabled = booleanPreferencesKey("background_updates")
    private val lock = Mutex()
    private var schedule: Schedule? = null
    val state = MutableStateFlow<ScheduleState?>(null)
    val background = MutableStateFlow(true)
    val transport: WatchTransport = NoOpWatchTransport

    suspend fun refresh(context: Context, setting: Boolean? = null) = withContext(Dispatchers.IO) {
        lock.withLock {
            val app = context.applicationContext
            if (setting != null) app.settings.edit { it[enabled] = setting }
            val active = app.settings.data.first()[enabled] ?: true
            val timetable = schedule ?: app.assets.open("schedule.json")
                .bufferedReader().use { Schedule(it.readText()) }.also { schedule = it }
            val snapshot = timetable.at(Instant.now())
            val alarm = app.getSystemService(AlarmManager::class.java)
            val operation = PendingIntent.getBroadcast(app, 0,
                Intent(app, RefreshReceiver::class.java).setAction("org.schoolface.companion.BOUNDARY"),
                PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
            if (active) alarm.set(AlarmManager.RTC_WAKEUP, snapshot.nextWake.toEpochMilli(), operation)
            else alarm.cancel(operation)
            background.value = active
            state.value = snapshot
        }
    }
}

class RefreshReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pending = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                ScheduleRuntime.refresh(context.applicationContext)
            } catch (error: Exception) {
                android.util.Log.e("SchoolFace", "Unable to refresh schedule", error)
            } finally {
                pending.finish()
            }
        }
    }
}

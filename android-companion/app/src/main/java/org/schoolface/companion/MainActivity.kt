package org.schoolface.companion

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

private val schoolColors = darkColorScheme(
    background = Color(0xFF0C0D16), surface = Color(0xFF0C0D16),
    primary = Color(0xFF8B7CFF), onPrimary = Color(0xFF0C0D16)
)

class MainActivity : ComponentActivity() {
    private var message by mutableStateOf<String?>(null)

    private fun refresh(setting: Boolean? = null) {
        lifecycleScope.launch {
            message = null
            try {
                ScheduleRuntime.refresh(applicationContext, setting)
            } catch (error: java.util.concurrent.CancellationException) {
                throw error
            } catch (error: Exception) {
                message = "Could not refresh the schedule."
                android.util.Log.e("SchoolFace", "Refresh failed", error)
            }
        }
    }

    override fun onResume() {
        super.onResume()
        refresh()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val state by ScheduleRuntime.state.collectAsState()
            val background by ScheduleRuntime.background.collectAsState()
            MaterialTheme(colorScheme = schoolColors) {
                Scaffold { insets ->
                    Column(Modifier.fillMaxSize().padding(insets).verticalScroll(rememberScrollState())
                        .padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Text("SchoolFace Companion", style = MaterialTheme.typography.headlineSmall)
                        val snapshot = state
                        if (snapshot == null) Text("Loading schedule…") else {
                            Text(snapshot.phase.title, color = schoolColors.primary)
                            snapshot.current?.let {
                                Text(it.subject, style = MaterialTheme.typography.headlineMedium)
                                Text("Lesson ${it.number} · ${it.start}–${it.end}")
                            }
                            Text("Next: ${snapshot.next?.subject ?: "—"}")
                            snapshot.remainingSeconds?.let {
                                Text("${(it + 59) / 60} min remaining at last refresh")
                            }
                            snapshot.progress?.let { value ->
                                LinearProgressIndicator(progress = { value }, modifier = Modifier.fillMaxWidth())
                            }
                        }
                        HorizontalDivider()
                        Text("Watch: ${ScheduleRuntime.transport.getStatus()}")
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Button(onClick = { refresh() }) { Text("Refresh") }
                            OutlinedButton(onClick = {
                                message = "Update unavailable. Watch transfer is unsupported."
                            }) { Text("Test Update") }
                        }
                        message?.let { Text(it) }
                        Row(horizontalArrangement = Arrangement.spacedBy(12.dp),
                            verticalAlignment = androidx.compose.ui.Alignment.CenterVertically) {
                            Switch(checked = background, onCheckedChange = { refresh(it) })
                            Text("Background updates")
                        }
                        Text("School time: Europe/Kyiv", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        }
    }
}

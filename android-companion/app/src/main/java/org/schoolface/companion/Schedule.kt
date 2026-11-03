package org.schoolface.companion

import java.time.*
import java.util.Locale
import org.json.JSONObject

enum class Phase(val title: String) {
    BEFORE("Before School"), CLASS("Current Class"), BREAK("Break Time"),
    FINISHED("School Finished"), WEEKEND("No Classes Today")
}

data class Lesson(val number: Int, val subject: String, val start: LocalTime, val end: LocalTime)
data class ScheduleState(
    val phase: Phase, val current: Lesson?, val next: Lesson?,
    val remainingSeconds: Long?, val progress: Float?, val nextWake: Instant
)

class Schedule(text: String) {
    private val json = JSONObject(text)
    val zone: ZoneId = ZoneId.of(json.getString("timezone"))

    private fun lessons(date: LocalDate): List<Lesson> {
        val day = date.dayOfWeek.name.lowercase(Locale.ROOT)
        val subjects = json.getJSONObject("days").getJSONArray(day)
        val bells = json.getJSONArray("bells")
        val rotation = json.getJSONObject("rotation")
        return List(subjects.length()) { index ->
            val slot = bells.getJSONArray(index)
            val subject = if (day == rotation.getString("day") && index + 1 == rotation.getInt("period")) {
                val anchor = LocalDate.parse(rotation.getString("anchor"))
                val week = Math.floorDiv(date.toEpochDay() - anchor.toEpochDay(), 7L)
                val choices = rotation.getJSONArray("subjects")
                choices.getString(Math.floorMod(week, choices.length().toLong()).toInt())
            } else subjects.getString(index)
            Lesson(index + 1, subject, LocalTime.parse(slot.getString(0)), LocalTime.parse(slot.getString(1)))
        }
    }

    fun at(now: Instant): ScheduleState {
        val date = now.atZone(zone).toLocalDate()
        val lessons = lessons(date)
        fun instant(time: LocalTime) = date.atTime(time).atZone(zone).toInstant()
        fun state(phase: Phase, current: Lesson?, next: Lesson?, end: Instant, start: Instant? = null): ScheduleState {
            val remaining = Duration.between(now, end)
            val seconds = remaining.seconds + if (remaining.nano > 0) 1 else 0
            val progress = start?.let {
                (Duration.between(it, now).toMillis().toDouble() /
                    Duration.between(it, end).toMillis()).toFloat().coerceIn(0f, 1f)
            }
            return ScheduleState(phase, current, next, seconds, progress, end)
        }
        lessons.forEachIndexed { index, lesson ->
            val start = instant(lesson.start)
            val end = instant(lesson.end)
            if (now < start) {
                val previous = lessons.getOrNull(index - 1)
                return state(if (previous == null) Phase.BEFORE else Phase.BREAK,
                    null, lesson, start, previous?.let { instant(it.end) })
            }
            if (now < end) return state(Phase.CLASS, lesson, lessons.getOrNull(index + 1), end, start)
        }
        return ScheduleState(if (lessons.isEmpty()) Phase.WEEKEND else Phase.FINISHED,
            null, null, null, null, date.plusDays(1).atStartOfDay(zone).toInstant())
    }
}

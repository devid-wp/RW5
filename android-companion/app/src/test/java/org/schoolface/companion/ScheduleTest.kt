package org.schoolface.companion

import java.io.File
import java.time.*
import org.junit.Assert.*
import org.junit.Test

class ScheduleTest {
    private val schedule = Schedule(File(System.getProperty("schoolface.schedule")!!).readText())
    private fun instant(value: String) = LocalDateTime.parse(value).atZone(schedule.zone).toInstant()
    private fun at(value: String) = schedule.at(instant(value))

    @Test fun lessonBoundaries() {
        assertEquals(Phase.BEFORE, at("2026-11-02T08:59:59").phase)
        val first = at("2026-11-02T09:00")
        assertEquals("Biology", first.current?.subject)
        assertEquals(1, first.current?.number)
        assertEquals(2700L, first.remainingSeconds)
        assertEquals(Phase.BREAK, at("2026-11-02T09:45").phase)
        assertEquals(Phase.FINISHED, at("2026-11-02T15:40").phase)
        assertEquals(8, at("2026-11-04T16:34").current?.number)
    }

    @Test fun breakProgressAndNextLesson() {
        val state = at("2026-11-02T09:50")
        assertEquals(Phase.BREAK, state.phase)
        assertEquals("History", state.next?.subject)
        assertEquals(0.5f, state.progress!!, 0.001f)
        assertEquals("History", at("2026-11-02T09:55").current?.subject)
    }

    @Test fun rotationBeforeAndAfterAnchor() {
        for ((date, subject) in listOf("10-29" to "Algebra", "11-05" to "World Literature",
            "11-12" to "Algebra", "11-19" to "World Literature", "11-26" to "Algebra")) {
            assertEquals(subject, at("2026-${date}T12:00").current?.subject)
        }
    }

    @Test fun weekendAndMidnight() {
        assertEquals(Phase.WEEKEND, at("2026-11-07T12:00").phase)
        val sunday = at("2026-11-08T23:59:59")
        assertEquals(Phase.WEEKEND, sunday.phase)
        assertEquals(instant("2026-11-09T00:00"), sunday.nextWake)
        assertEquals(Phase.BEFORE, schedule.at(sunday.nextWake).phase)
    }

    @Test fun phoneZoneDoesNotChangeKyivSchedule() {
        val utc = ZonedDateTime.parse("2026-11-02T07:00Z")
        assertEquals("Biology", schedule.at(utc.toInstant()).current?.subject)
        assertEquals(schedule.at(utc.toInstant()),
            schedule.at(utc.withZoneSameInstant(ZoneId.of("America/New_York")).toInstant()))
        assertEquals("Biology", schedule.at(Instant.parse("2027-05-03T06:00:00Z")).current?.subject)
    }

    @Test fun nextWakeTracksCurrentBoundaryEvenAfterDelay() {
        assertEquals(instant("2026-11-02T09:00"), at("2026-11-02T08:00").nextWake)
        assertEquals(instant("2026-11-02T09:45"), at("2026-11-02T09:20").nextWake)
        assertEquals(instant("2026-11-02T09:55"), at("2026-11-02T09:51").nextWake)
        assertEquals(instant("2026-11-02T10:40"), at("2026-11-02T10:05").nextWake)
    }
}

plugins {
    id("com.android.application") version "8.7.3"
    id("org.jetbrains.kotlin.android") version "2.0.21"
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21"
}
android {
    namespace = "org.schoolface.companion"
    compileSdk = 35
    defaultConfig {
        applicationId = "org.schoolface.companion"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.1"
    }
    buildFeatures { compose = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    sourceSets["main"].assets.srcDir(layout.buildDirectory.dir("generated/scheduleAssets"))
}
val scheduleAssets by tasks.registering(Copy::class) {
    from(rootProject.file("../schedule.json"))
    into(layout.buildDirectory.dir("generated/scheduleAssets"))
}
tasks.named("preBuild") { dependsOn(scheduleAssets) }
dependencies {
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.compose.material3:material3:1.3.2")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.datastore:datastore-preferences:1.1.3")
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.json:json:20240303")
}
tasks.withType<Test>().configureEach {
    systemProperty("schoolface.schedule", rootProject.file("../schedule.json").absolutePath)
}

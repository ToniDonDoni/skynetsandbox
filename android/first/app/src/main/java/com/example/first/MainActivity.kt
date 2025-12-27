package com.example.first

import android.content.Context
import android.os.Bundle
import android.widget.SeekBar
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.edit
import com.example.first.databinding.ActivityMainBinding

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val preferences = getPreferences(Context.MODE_PRIVATE)

        val savedDarkMode = preferences.getBoolean(KEY_DARK_MODE, false)
        val savedNotifications = preferences.getBoolean(KEY_NOTIFICATIONS, true)
        val savedSync = preferences.getBoolean(KEY_SYNC, true)
        val savedVolume = preferences.getInt(KEY_VOLUME, 50)

        binding.switchDarkMode.isChecked = savedDarkMode
        binding.switchNotifications.isChecked = savedNotifications
        binding.switchSync.isChecked = savedSync
        binding.volumeSeekBar.progress = savedVolume
        binding.volumeValue.text = formatVolume(savedVolume)

        binding.switchDarkMode.setOnCheckedChangeListener { _, isChecked ->
            preferences.edit { putBoolean(KEY_DARK_MODE, isChecked) }
            updateStatus()
        }

        binding.switchNotifications.setOnCheckedChangeListener { _, isChecked ->
            preferences.edit { putBoolean(KEY_NOTIFICATIONS, isChecked) }
            updateStatus()
        }

        binding.switchSync.setOnCheckedChangeListener { _, isChecked ->
            preferences.edit { putBoolean(KEY_SYNC, isChecked) }
            updateStatus()
        }

        binding.volumeSeekBar.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                binding.volumeValue.text = formatVolume(progress)
                preferences.edit { putInt(KEY_VOLUME, progress) }
            }

            override fun onStartTrackingTouch(seekBar: SeekBar?) = Unit

            override fun onStopTrackingTouch(seekBar: SeekBar?) {
                updateStatus()
            }
        })

        updateStatus()
    }

    private fun formatVolume(value: Int): String = "$value%"

    private fun updateStatus() {
        val darkEnabled = if (binding.switchDarkMode.isChecked) "On" else "Off"
        val notificationsEnabled = if (binding.switchNotifications.isChecked) "On" else "Off"
        val syncEnabled = if (binding.switchSync.isChecked) "On" else "Off"

        binding.statusText.text = getString(
            R.string.status_template,
            darkEnabled,
            notificationsEnabled,
            syncEnabled
        )
    }

    companion object {
        private const val KEY_DARK_MODE = "pref_dark_mode"
        private const val KEY_NOTIFICATIONS = "pref_notifications"
        private const val KEY_SYNC = "pref_sync"
        private const val KEY_VOLUME = "pref_volume"
    }
}

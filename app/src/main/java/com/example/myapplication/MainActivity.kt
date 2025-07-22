package com.example.myapplication

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.media.MediaRecorder
import android.net.Uri
import android.os.Environment
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import java.io.File
import java.io.IOException
import java.net.NetworkInterface
import java.net.ServerSocket
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    private lateinit var btnRecord: Button
    private lateinit var tvStatus: TextView
    private var mediaRecorder: MediaRecorder? = null
    private var isRecording = false
    private var serverSocket: ServerSocket? = null
    private val executor = Executors.newSingleThreadExecutor()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        btnRecord = findViewById(R.id.btnRecord)
        tvStatus = findViewById(R.id.tvStatus)

        // Solicitar permisos
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED ||
            ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.RECORD_AUDIO, Manifest.permission.WRITE_EXTERNAL_STORAGE),
                1
            )
        }

        btnRecord.setOnClickListener {
            if (isRecording) {
                stopRecording()
            }
        }

        // Abrir automáticamente la app al iniciar
        openAppAutomatically()
        startSocketServer()
    }

    private fun openAppAutomatically() {
        val launchIntent = packageManager.getLaunchIntentForPackage(packageName)
        startActivity(launchIntent)
    }

    private fun getLocalIpAddress(): String? {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val intf = interfaces.nextElement()
                val addrs = intf.inetAddresses
                while (addrs.hasMoreElements()) {
                    val addr = addrs.nextElement()
                    if (!addr.isLoopbackAddress && addr.hostAddress.indexOf(':') < 0) {
                        return addr.hostAddress
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return null
    }

    private fun startSocketServer() {
        executor.execute {
            try {
                serverSocket = ServerSocket(12345)
                val ipAddress = getLocalIpAddress()

                runOnUiThread {
                    tvStatus.text = "Servidor: $ipAddress:12345\nEsperando comando..."
                }

                while (true) {
                    val socket = serverSocket?.accept()
                    val input = socket?.getInputStream()?.bufferedReader()
                    val message = input?.readLine()

                    if (message?.contains("camara tapada") == true) {
                        runOnUiThread {
                            btnRecord.isEnabled = true
                            startRecording()
                        }
                    }
                    socket?.close()
                }
            } catch (e: Exception) {
                e.printStackTrace()
                runOnUiThread {
                    tvStatus.text = "Error: ${e.message}"
                }
            }
        }
    }

    private fun startRecording() {
        try {
            val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
            val outputFile = File(downloadsDir, "audio_record_${System.currentTimeMillis()}.3gp")

            mediaRecorder = MediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP)
                setOutputFile(outputFile.absolutePath)
                setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB)

                prepare()
                start()

                isRecording = true
                btnRecord.text = "Detener grabación"
                tvStatus.text = "🔴 Grabando audio..."

                Toast.makeText(
                    this@MainActivity,
                    "Grabación iniciada",
                    Toast.LENGTH_SHORT
                ).show()
            }
        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(this, "Error al grabar: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun stopRecording() {
        mediaRecorder?.apply {
            try {
                stop()
                release()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
        mediaRecorder = null

        isRecording = false
        btnRecord.text = "Iniciar grabación"
        btnRecord.isEnabled = false
        tvStatus.text = "✅ Grabación guardada\nEsperando comando..."

        Toast.makeText(
            this,
            "Audio guardado en Downloads",
            Toast.LENGTH_SHORT
        ).show()
    }

    override fun onDestroy() {
        super.onDestroy()
        serverSocket?.close()
        executor.shutdown()
        mediaRecorder?.release()
        mediaRecorder = null
    }
}
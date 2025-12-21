package com.paystack.sampleandroidwebview

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient

class WebviewActivity : AppCompatActivity() {

    // the authorization URL should be dynamically loaded from your backend server
    private val authorizationUrl: String
        get() = "https://checkout.paystack.com/n0yw50p3agba6qp"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_webview)

        loadCheckout()
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun loadCheckout() {
        val webView: WebView = findViewById(R.id.webview)
        webView.settings.apply {
            javaScriptEnabled = true
            javaScriptCanOpenWindowsAutomatically = true
            domStorageEnabled = true
        }

        webView.webViewClient = object:  WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url: Uri? = request?.url
                when {
                    url.toString().contains("tel") -> {
                        dialPhoneNumber(url)
                        return true
                    }
                    // handle 3DS, onPageFinished should handle it as well
                    url.toString() == "https://standard.paystack.co/close" -> {
                        return true
                    }
                }

                return false
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                if(url != authorizationUrl) {
                    goBack()
                }
            }
        }

        webView.loadUrl(authorizationUrl)
    }

    fun goBack() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
    }

    fun dialPhoneNumber(phoneNumber: Uri?) {
        val intent = Intent(Intent.ACTION_DIAL).apply {
            data = phoneNumber
        }
        if (intent.resolveActivity(packageManager) != null) {
            startActivity(intent)
        }
    }
}
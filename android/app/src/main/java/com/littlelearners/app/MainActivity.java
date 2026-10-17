package com.littlelearners.app;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.webkit.WebViewAssetLoader;

import java.util.Locale;

/**
 * Nuzaim Learns: wraps the web app (assets/index.html) in a WebView.
 * The page is served from https://appassets.androidplatform.net so that
 * embedded YouTube videos get a proper https origin.
 */
public class MainActivity extends Activity {

    private static final String HOST = "appassets.androidplatform.net";
    private static final String START_URL = "https://" + HOST + "/assets/index.html";

    private WebView webView;
    private FrameLayout root;
    private View customView;
    private WebChromeClient.CustomViewCallback customViewCallback;
    private WebChromeClient chromeClient;
    private TextToSpeech tts;
    private boolean ttsReady = false;
    private volatile boolean linksLocked = true;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(0xff, 0xf8, 0xec));
        webView = new WebView(this);
        root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setSupportZoom(false);

        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .setDomain(HOST)
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                // Pages written for the speechSynthesis API (not present in WebView) get the phone's voice instead.
                view.evaluateJavascript(
                    "if(!window.speechSynthesis&&window.AndroidTTS){" +
                    "window.SpeechSynthesisUtterance=function(t){this.text=t;this.lang='';this.rate=1;this.pitch=1;};" +
                    "window.speechSynthesis={speak:function(u){AndroidTTS.speakLang(u.text,u.lang||'',u.rate||1,u.pitch||1);}," +
                    "cancel:function(){AndroidTTS.stop();},speaking:false,pending:false,getVoices:function(){return[];}};}", null);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (!request.isForMainFrame()) return false;
                Uri uri = request.getUrl();
                if (HOST.equals(uri.getHost())) return false;
                // Parent lock on: never leave the app (e.g. tapping the YouTube logo in a video).
                if (linksLocked) return true;
                // Any outside link (e.g. "open on YouTube") opens in the phone's browser/YouTube app.
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, uri));
                } catch (Exception ignored) { }
                return true;
            }
        });

        chromeClient = new WebChromeClient() {
            @Override
            public void onShowCustomView(View view, CustomViewCallback callback) {
                if (customView != null) { callback.onCustomViewHidden(); return; }
                customView = view;
                customViewCallback = callback;
                root.addView(view, new FrameLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
                webView.setVisibility(View.GONE);
            }

            @Override
            public void onHideCustomView() {
                if (customView == null) return;
                root.removeView(customView);
                customView = null;
                webView.setVisibility(View.VISIBLE);
                if (customViewCallback != null) customViewCallback.onCustomViewHidden();
                customViewCallback = null;
            }
        };
        webView.setWebChromeClient(chromeClient);

        tts = new TextToSpeech(this, status -> {
            if (status == TextToSpeech.SUCCESS) {
                tts.setLanguage(Locale.US);
                tts.setSpeechRate(0.85f);
                tts.setPitch(1.2f);
                ttsReady = true;
            }
        });
        webView.addJavascriptInterface(new SpeechBridge(), "AndroidTTS");

        if (savedInstanceState != null) {
            webView.restoreState(savedInstanceState);
        } else {
            webView.loadUrl(START_URL);
        }
    }

    /** Lets the web app read instructions aloud (WebView has no built-in speech). */
    private class SpeechBridge {
        private Locale pick(String lang) {
            Locale loc = (lang == null || lang.isEmpty()) ? Locale.US : Locale.forLanguageTag(lang);
            if (tts.isLanguageAvailable(loc) >= TextToSpeech.LANG_AVAILABLE) return loc;
            Locale base = new Locale(loc.getLanguage());   // e.g. bn-BD missing -> try bn
            if (tts.isLanguageAvailable(base) >= TextToSpeech.LANG_AVAILABLE) return base;
            return Locale.US;
        }

        private void say(String text, Locale loc, float rate, float pitch) {
            // Settings are applied fresh for every utterance, so languages never leak between calls.
            tts.setLanguage(loc);
            tts.setSpeechRate(rate);
            tts.setPitch(pitch);
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "ll");
        }

        @JavascriptInterface
        public void speak(String text) {
            if (ttsReady && text != null) say(text, Locale.US, 0.85f, 1.2f);
        }

        @JavascriptInterface
        public void speakLang(String text, String lang, float rate, float pitch) {
            if (ttsReady && text != null) say(text, pick(lang), rate, pitch);
        }

        @JavascriptInterface
        public boolean hasLang(String lang) {
            if (!ttsReady || lang == null) return false;
            Locale loc = Locale.forLanguageTag(lang);
            return tts.isLanguageAvailable(loc) >= TextToSpeech.LANG_AVAILABLE
                || tts.isLanguageAvailable(new Locale(loc.getLanguage())) >= TextToSpeech.LANG_AVAILABLE;
        }

        @JavascriptInterface
        public boolean isReady() { return ttsReady; }

        @JavascriptInterface
        public void setLocked(boolean locked) { linksLocked = locked; }

        @JavascriptInterface
        public void stop() {
            if (ttsReady) tts.stop();
        }
    }

    @Override
    public void onBackPressed() {
        if (customView != null) {
            chromeClient.onHideCustomView();
            return;
        }
        // Ask the page to close a video or return home first; exit only from the home screen.
        webView.evaluateJavascript("(window.androidBack && window.androidBack()) ? 'y' : 'n'", value -> {
            if (value == null || !value.contains("y")) MainActivity.super.onBackPressed();
        });
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        webView.saveState(outState);
    }

    @Override
    protected void onPause() {
        super.onPause();
        webView.onPause();
        if (ttsReady) tts.stop();
    }

    @Override
    protected void onResume() {
        super.onResume();
        webView.onResume();
    }

    @Override
    protected void onDestroy() {
        if (tts != null) tts.shutdown();
        if (webView != null) webView.destroy();
        super.onDestroy();
    }
}

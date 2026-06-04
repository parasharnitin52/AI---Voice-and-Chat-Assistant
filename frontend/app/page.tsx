"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";
import VoiceButton from "../components/VoiceButton";
import ChatHistory from "../components/ChatHistory";
import TicketModal from "../components/TicketModal";
import {
  transcribeAudio,
  sendChat,
  generateSessionId,
  ChatMessage,
  PRODUCT_ICONS,
  PRODUCT_LABELS,
} from "../lib/api";
import styles from "./page.module.css";

type AppStatus = "idle" | "recording" | "transcribing" | "thinking" | "speaking" | "error";

export default function HomePage() {
  const [sessionId] = useState(() => generateSessionId());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState<AppStatus>("idle");
  const [statusText, setStatusText] = useState("");
  const [transcript, setTranscript] = useState("");
  const [productDetected, setProductDetected] = useState("unknown");
  const [intentDetected, setIntentDetected] = useState<string | undefined>();
  const [languageDetected, setLanguageDetected] = useState("english");
  const [manualProduct, setManualProduct] = useState<string | null>(null);
  const [manualLanguage, setManualLanguage] = useState<string | null>(null);
  const [suggestTicket, setSuggestTicket] = useState(false);
  const [showTicketModal, setShowTicketModal] = useState(false);
  const [ticketSuccess, setTicketSuccess] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const speechRef = useRef<SpeechSynthesisUtterance | null>(null);
  const speechQueueRef = useRef<SpeechSynthesisUtterance[]>([]);

  const handleProductSelect = (productKey: string) => {
    setProductDetected(productKey);
    setManualProduct(productKey);
  };

  const handleLanguageSelect = (langKey: string) => {
    const lang = langKey.toLowerCase();
    setLanguageDetected(lang);
    setManualLanguage(lang);
  };

  useEffect(() => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;

    const loadVoices = () => {
      setAvailableVoices(window.speechSynthesis.getVoices());
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, []);

  const pickVoice = useCallback((lang: string) => {
    const byLang = (prefix: string) =>
      availableVoices.filter((voice) => voice.lang.toLowerCase().startsWith(prefix));
    const preferNatural = (voices: SpeechSynthesisVoice[]) =>
      voices.find((voice) => /natural|online|neural|aria|jenny|guy|heera|ravi|google|microsoft/i.test(voice.name))
      || voices.find((voice) => /microsoft|google/i.test(voice.name))
      || voices.find((voice) => !voice.localService)
      || voices.find((voice) => voice.localService)
      || voices[0];

    if (lang === "hindi") {
      return preferNatural(byLang("hi"));
    }

    if (lang === "hinglish") {
      return preferNatural(byLang("en-in")) || preferNatural(byLang("hi")) || preferNatural(byLang("en"));
    }

    return preferNatural(byLang("en-in")) || preferNatural(byLang("en-us")) || preferNatural(byLang("en"));
  }, [availableVoices]);

  // ── Text-to-speech ──────────────────────────────────────────────
  const speak = useCallback((text: string, lang: string) => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    speechQueueRef.current = [];

    const chunks = text
      .replace(/\s+/g, " ")
      .match(/[^.!?।]+[.!?।]?/g)
      ?.map((chunk) => chunk.trim())
      .filter(Boolean) || [text];
    const voice = pickVoice(lang);

    const speakChunk = (index: number) => {
      const chunk = chunks[index];
      if (!chunk) {
        setIsSpeaking(false);
        setStatus("idle");
        setStatusText("");
        return;
      }

      const utter = new SpeechSynthesisUtterance(chunk);
      utter.lang = lang === "hindi" ? "hi-IN" : "en-IN";
      utter.rate = lang === "hindi" ? 0.86 : 0.88;
      utter.pitch = 0.98;
      utter.volume = 1;
      if (voice) utter.voice = voice;

      utter.onstart = () => {
        setIsSpeaking(true);
        setStatus("speaking");
        setStatusText("Speaking...");
      };
      utter.onend = () => window.setTimeout(() => speakChunk(index + 1), 120);
      utter.onerror = () => {
        setIsSpeaking(false);
        setStatus("idle");
        setStatusText("");
      };

      speechRef.current = utter;
      speechQueueRef.current[index] = utter;
      window.speechSynthesis.speak(utter);
    };

    const utter = new SpeechSynthesisUtterance("");
    speakChunk(0);
    utter.onstart = () => { setIsSpeaking(true); setStatus("speaking"); setStatusText("Speaking…"); };

  }, [pickVoice]);

  const stopSpeaking = () => {
    window.speechSynthesis?.cancel();
    speechQueueRef.current = [];
    setIsSpeaking(false);
    setStatus("idle");
    setStatusText("");
  };

  // ── Handle audio from VoiceButton ──────────────────────────────
  const handleAudioReady = useCallback(async (blob: Blob) => {
    setErrorMsg("");
    setTranscript("");

    // Prevent sending tiny/empty files (e.g. accidental clicks)
    if (blob.size < 800) {
      setStatus("idle");
      setErrorMsg("Please hold the button for at least one second and speak clearly.");
      return;
    }

    try {
      // Step 1: Transcribe
      setStatus("transcribing");
      setStatusText("Transcribing your voice…");
      const tResult = await transcribeAudio(blob, manualLanguage || undefined);
      const userText = tResult.transcript;

      if (!userText.trim()) {
        setStatus("idle");
        setStatusText("");
        setErrorMsg("Could not understand audio. Please try again.");
        return;
      }

      setTranscript(userText);

      // Step 2: Chat
      setStatus("thinking");
      setStatusText("AI is thinking…");
      const chatResult = await sendChat(
        sessionId,
        userText,
        undefined,
        undefined,
        manualProduct || undefined,
        manualLanguage || undefined
      );

      setMessages(chatResult.conversation_history);
      setProductDetected(chatResult.product_detected);
      setIntentDetected(chatResult.intent_detected);
      setLanguageDetected(chatResult.language_detected);
      setSuggestTicket(chatResult.suggest_ticket);
      setTranscript("");

      // Step 3: Speak response
      speak(chatResult.response, chatResult.language_detected);
    } catch (err: unknown) {
      setStatus("error");
      const msg = err instanceof Error ? err.message : "Something went wrong.";
      setErrorMsg(msg);
      setStatusText("");
      setTimeout(() => setStatus("idle"), 3000);
    }
  }, [manualLanguage, manualProduct, sessionId, speak]);

  // ── Text input fallback ─────────────────────────────────────────
  const [textInput, setTextInput] = useState("");
  const handleTextSend = async () => {
    if (!textInput.trim()) return;
    const msg = textInput.trim();
    setTextInput("");
    setErrorMsg("");

    try {
      setStatus("thinking");
      setStatusText("AI is thinking…");
      const chatResult = await sendChat(
        sessionId,
        msg,
        undefined,
        undefined,
        manualProduct || undefined,
        manualLanguage || undefined
      );
      setMessages(chatResult.conversation_history);
      setProductDetected(chatResult.product_detected);
      setIntentDetected(chatResult.intent_detected);
      setLanguageDetected(chatResult.language_detected);
      setSuggestTicket(chatResult.suggest_ticket);
      speak(chatResult.response, chatResult.language_detected);
    } catch (err: unknown) {
      const m = err instanceof Error ? err.message : "Error";
      setErrorMsg(m);
      setStatus("idle");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleTextSend(); }
  };

  const handleNewSession = () => {
    window.location.reload();
  };

  const isProcessing = status === "transcribing" || status === "thinking";

  return (
    <div className={styles.page}>
      {/* ── Header ─────────────────────────────────── */}
      <header className={styles.header}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>⚡</span>
          <span className={styles.logoText}>Electro<strong>Serv</strong></span>
        </div>
        <div className={styles.headerRight}>
          <div className={styles.statusPill}>
            <span className={`${styles.dot} ${status === "idle" ? styles.green : status === "error" ? styles.red : styles.amber}`} />
            <span>{status === "idle" ? "Ready" : status === "speaking" ? "Speaking" : "Processing"}</span>
          </div>
          <button className="btn btn-ghost" id="new-session-btn" onClick={handleNewSession}>
            🔄 New Chat
          </button>
        </div>
      </header>

      <main className={styles.main}>
        {/* ── Left: Chat Panel ─────────────────────── */}
        <section className={`${styles.chatPanel} glass`}>
          <ChatHistory
            messages={messages}
            productDetected={productDetected}
            intentDetected={intentDetected}
            languageDetected={languageDetected}
            isTyping={isProcessing}
          />

          {/* Live transcript preview */}
          {transcript && (
            <div className={styles.transcriptBanner}>
              <span className={styles.transcriptLabel}>You said:</span>
              <span className={styles.transcriptText}>{transcript}</span>
            </div>
          )}

          {/* Error */}
          {errorMsg && (
            <div className={styles.errorBanner}>
              ⚠️ {errorMsg}
            </div>
          )}

          {/* Text input */}
          <div className={styles.textBar}>
            <input
              className={`${styles.textInput} input`}
              placeholder="Or type your message here…"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isProcessing || isSpeaking}
              id="text-input"
            />
            <button
              className={`btn btn-primary ${styles.sendBtn}`}
              onClick={handleTextSend}
              disabled={!textInput.trim() || isProcessing || isSpeaking}
              id="send-text-btn"
            >
              ➤
            </button>
          </div>
        </section>

        {/* ── Right: Controls ──────────────────────── */}
        <aside className={styles.controls}>
          {/* Voice section */}
          <div className={`${styles.voiceCard} glass`}>
            <h2 className={styles.voiceTitle}>Voice Input</h2>
            <p className={styles.voiceSubtitle}>Hold the button and speak clearly</p>

            <VoiceButton
              onAudioReady={handleAudioReady}
              disabled={isSpeaking}
              isProcessing={isProcessing}
            />

            {/* Status text */}
            {statusText && (
              <div className={styles.statusBar}>
                <span className={styles.statusSpinner} />
                <span>{statusText}</span>
              </div>
            )}

            {/* Stop speaking */}
            {isSpeaking && (
              <button className="btn btn-danger" onClick={stopSpeaking} id="stop-speaking-btn">
                ⏹ Stop Speaking
              </button>
            )}
          </div>

          {/* Products */}
          <div className={`${styles.productsCard} glass`}>
            <h3 className={styles.cardTitle}>Supported Products</h3>
            <div className={styles.productList}>
              {["ac", "washing_machine", "microwave"].map((p) => (
                <div
                  key={p}
                  className={`${styles.productItem} ${productDetected === p ? styles.productActive : ""}`}
                  onClick={() => handleProductSelect(p)}
                >
                  <span className={styles.productEmoji}>{PRODUCT_ICONS[p]}</span>
                  <span className={styles.productName}>{PRODUCT_LABELS[p]}</span>
                  {productDetected === p && <span className={styles.activeTag}>Active</span>}
                </div>
              ))}
            </div>
          </div>

          {/* Languages */}
          <div className={`${styles.langCard} glass`}>
            <h3 className={styles.cardTitle}>Languages</h3>
            <div className={styles.langList}>
              {[["🇬🇧", "English"], ["🇮🇳", "Hindi"], ["🌐", "Hinglish"]].map(([flag, lang]) => (
                <div 
                  key={lang} 
                  className={`${styles.langItem} ${languageDetected?.toLowerCase() === lang.toLowerCase() ? styles.langActive : ""}`}
                  onClick={() => handleLanguageSelect(lang)}
                >
                  <span>{flag}</span> <span>{lang}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Ticket suggestion */}
          {suggestTicket && !ticketSuccess && (
            <div className={`${styles.ticketBanner} glass`}>
              <p className={styles.ticketBannerText}>
                🎫 Issue unresolved? Create a service ticket and we'll send a technician.
              </p>
              <button
                className="btn btn-primary"
                onClick={() => setShowTicketModal(true)}
                id="create-ticket-btn"
                style={{ width: "100%" }}
              >
                Create Service Ticket
              </button>
            </div>
          )}

          {/* Ticket success */}
          {ticketSuccess && (
            <div className={styles.ticketSuccess}>
              ✅ Ticket <strong>{ticketSuccess}</strong> created!<br />
              <span>A technician will contact you within 24 hours.</span>
            </div>
          )}
        </aside>
      </main>

      {/* ── Ticket Modal ─────────────────────────── */}
      {showTicketModal && (
        <TicketModal
          sessionId={sessionId}
          productDetected={productDetected}
          intentDetected={intentDetected}
          onClose={() => setShowTicketModal(false)}
          onSuccess={(ticketNo) => {
            setTicketSuccess(ticketNo);
            setShowTicketModal(false);
            setSuggestTicket(false);
          }}
        />
      )}
    </div>
  );
}

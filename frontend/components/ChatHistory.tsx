"use client";

import React, { useEffect, useRef } from "react";
import { ChatMessage, PRODUCT_ICONS, PRODUCT_LABELS } from "../lib/api";
import styles from "./ChatHistory.module.css";

interface Props {
  messages: ChatMessage[];
  productDetected: string;
  intentDetected?: string;
  languageDetected: string;
  isTyping?: boolean;
}

const LANG_LABELS: Record<string, string> = {
  english: "🇬🇧 English",
  hindi: "🇮🇳 Hindi",
  hinglish: "🌐 Hinglish",
};

export default function ChatHistory({
  messages,
  productDetected,
  intentDetected,
  languageDetected,
  isTyping,
}: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const formatTime = (ts?: string) => {
    if (!ts) return "";
    const d = new Date(ts + "Z");
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className={styles.container}>
      {/* Context bar */}
      {productDetected && productDetected !== "unknown" && (
        <div className={styles.contextBar}>
          <span className={styles.contextItem}>
            {PRODUCT_ICONS[productDetected]}&nbsp;
            <strong>{PRODUCT_LABELS[productDetected] || productDetected}</strong>
          </span>
          {intentDetected && (
            <span className={`${styles.contextItem} ${styles.intent}`}>
              🎯 {intentDetected.replace(/_/g, " ")}
            </span>
          )}
          <span className={`${styles.contextItem} ${styles.lang}`}>
            {LANG_LABELS[languageDetected] || languageDetected}
          </span>
        </div>
      )}

      {/* Messages */}
      <div className={styles.messages} id="chat-messages">
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>🎙️</div>
            <p className={styles.emptyTitle}>Hold the mic button and speak</p>
            <p className={styles.emptySub}>
              Supports English, Hindi &amp; Hinglish
            </p>
            <div className={styles.productGrid}>
              {["ac", "washing_machine", "microwave"].map((p) => (
                <div key={p} className={styles.productChip}>
                  {PRODUCT_ICONS[p]} {PRODUCT_LABELS[p]}
                </div>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`${styles.msgRow} ${msg.role === "user" ? styles.userRow : styles.assistantRow} fade-in-up`}
          >
            {msg.role === "assistant" && (
              <div className={styles.avatar} aria-label="AI agent">
                ⚡
              </div>
            )}
            <div className={`${styles.bubble} ${msg.role === "user" ? styles.userBubble : styles.aiBubble}`}>
              <p className={styles.bubbleText}>{msg.content}</p>
              {msg.timestamp && (
                <span className={styles.timestamp}>{formatTime(msg.timestamp)}</span>
              )}
            </div>
            {msg.role === "user" && (
              <div className={styles.avatar} aria-label="You">
                👤
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className={`${styles.msgRow} ${styles.assistantRow}`}>
            <div className={styles.avatar}>⚡</div>
            <div className={`${styles.bubble} ${styles.aiBubble} ${styles.typingBubble}`}>
              <span className={styles.dot} />
              <span className={styles.dot} style={{ animationDelay: "0.15s" }} />
              <span className={styles.dot} style={{ animationDelay: "0.3s" }} />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}

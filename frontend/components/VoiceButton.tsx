"use client";

import React, { useRef, useState, useCallback } from "react";
import styles from "./VoiceButton.module.css";

interface Props {
  onAudioReady: (blob: Blob) => void;
  disabled?: boolean;
  isProcessing?: boolean;
}

export default function VoiceButton({ onAudioReady, disabled, isProcessing }: Props) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";
      const recorder = new MediaRecorder(stream, { mimeType });
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        onAudioReady(blob);
        stream.getTracks().forEach((t) => t.stop());
      };

      recorder.start(100);
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
      alert("Please allow microphone access to use voice input.");
    }
  }, [onAudioReady]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const handlePointerDown = (e: React.PointerEvent) => {
    e.preventDefault();
    if (!disabled && !isProcessing) startRecording();
  };
  const handlePointerUp = (e: React.PointerEvent) => {
    e.preventDefault();
    if (isRecording) stopRecording();
  };

  const isActive = isRecording;

  return (
    <div className={styles.wrapper}>
      {/* Outer pulse rings */}
      {isActive && (
        <>
          <span className={`${styles.ring} ${styles.ring1}`} />
          <span className={`${styles.ring} ${styles.ring2}`} />
          <span className={`${styles.ring} ${styles.ring3}`} />
        </>
      )}

      <button
        className={`${styles.btn} ${isActive ? styles.recording : ""} ${isProcessing ? styles.processing : ""}`}
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        disabled={disabled || isProcessing}
        aria-label={isRecording ? "Release to send" : "Hold to speak"}
        id="voice-record-btn"
      >
        {isProcessing ? (
          <span className={styles.spinner} />
        ) : isRecording ? (
          <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
            <rect x="6" y="6" width="12" height="12" rx="2" />
          </svg>
        ) : (
          <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4z" />
            <path d="M19 10v2a7 7 0 0 1-14 0v-2H3v2a9 9 0 0 0 8 8.94V23h2v-2.06A9 9 0 0 0 21 12v-2h-2z" />
          </svg>
        )}
      </button>

      {/* Wave bars when recording */}
      {isActive && (
        <div className={styles.waves}>
          {[...Array(5)].map((_, i) => (
            <span key={i} className={styles.bar} style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
      )}

      <p className={styles.hint}>
        {isProcessing ? "Processing…" : isRecording ? "Release to send" : "Hold to speak"}
      </p>
    </div>
  );
}

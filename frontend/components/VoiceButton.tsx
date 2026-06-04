"use client";

import React, { useRef, useState, useCallback } from "react";
import styles from "./VoiceButton.module.css";

interface Props {
  onAudioReady: (blob: Blob) => void;
  disabled?: boolean;
  isProcessing?: boolean;
}

const MIN_RECORDING_MS = 700;

function getSupportedMimeType(): string {
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/ogg;codecs=opus",
  ];

  return candidates.find((type) => MediaRecorder.isTypeSupported(type)) || "";
}

export default function VoiceButton({ onAudioReady, disabled, isProcessing }: Props) {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const recordingStartedAtRef = useRef(0);

  const isRecordingRequested = useRef(false);

  const startRecording = useCallback(async () => {
    try {
      isRecordingRequested.current = true;
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // If user released the button while we were getting user media, cancel!
      if (!isRecordingRequested.current) {
        stream.getTracks().forEach((t) => t.stop());
        return;
      }

      const mimeType = getSupportedMimeType();
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);
      chunksRef.current = [];
      streamRef.current = stream;
      recordingStartedAtRef.current = Date.now();

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const type = recorder.mimeType || mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type });
        const durationMs = Date.now() - recordingStartedAtRef.current;
        if (durationMs >= MIN_RECORDING_MS && blob.size > 0) {
          onAudioReady(blob);
        } else if (blob.size > 0) {
          onAudioReady(blob);
        }
        stream.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
        mediaRecorderRef.current = null;
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
      alert("Please allow microphone access to use voice input.");
      isRecordingRequested.current = false;
      setIsRecording(false);
    }
  }, [onAudioReady]);

  const stopRecording = useCallback(() => {
    isRecordingRequested.current = false;
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state === "recording") {
      const elapsedMs = Date.now() - recordingStartedAtRef.current;
      const stop = () => {
        if (recorder.state === "recording") {
          recorder.stop();
        }
      };

      if (elapsedMs < MIN_RECORDING_MS) {
        window.setTimeout(stop, MIN_RECORDING_MS - elapsedMs);
      } else {
        stop();
      }
    } else {
      streamRef.current?.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setIsRecording(false);
  }, []);

  const handlePointerDown = (e: React.PointerEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (!disabled && !isProcessing) {
      e.currentTarget.setPointerCapture(e.pointerId);
      startRecording();
    }
  };

  const handlePointerUp = (e: React.PointerEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (isRecording || isRecordingRequested.current) {
      try {
        e.currentTarget.releasePointerCapture(e.pointerId);
      } catch (err) {
        // ignore if already released
      }
      stopRecording();
    }
  };

  const handlePointerCancel = (e: React.PointerEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (isRecording || isRecordingRequested.current) {
      try {
        e.currentTarget.releasePointerCapture(e.pointerId);
      } catch (err) {
        // ignore
      }
      stopRecording();
    }
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
        onPointerCancel={handlePointerCancel}
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

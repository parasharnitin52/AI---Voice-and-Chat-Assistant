"use client";

import React, { useState } from "react";
import { createTicket, PRODUCT_LABELS } from "../lib/api";
import styles from "./TicketModal.module.css";

interface Props {
  sessionId: string;
  productDetected: string;
  intentDetected?: string;
  onClose: () => void;
  onSuccess: (ticketNumber: string) => void;
}

export default function TicketModal({
  sessionId,
  productDetected,
  intentDetected,
  onClose,
  onSuccess,
}: Props) {
  const [form, setForm] = useState({
    customer_name: "",
    phone_number: "",
    issue_description: "",
    product: productDetected !== "unknown" ? productDetected : "ac",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.customer_name.length < 2) { setError("Enter your full name."); return; }
    if (form.phone_number.length < 10) { setError("Enter a valid 10-digit phone number."); return; }
    if (form.issue_description.length < 10) { setError("Please describe the issue in detail."); return; }

    setLoading(true);
    try {
      const ticket = await createTicket({
        session_id: sessionId,
        customer_name: form.customer_name,
        phone_number: form.phone_number,
        product: form.product,
        issue_description: form.issue_description,
        intent: intentDetected,
      });
      onSuccess(ticket.ticket_number);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create ticket.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={`${styles.modal} glass fade-in-up`} role="dialog" aria-modal="true">
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <div className={styles.headerIcon}>🎫</div>
            <div>
              <h2 className={styles.title}>Create Service Ticket</h2>
              <p className={styles.subtitle}>A technician will contact you within 24 hours</p>
            </div>
          </div>
          <button className={styles.closeBtn} onClick={onClose} id="ticket-modal-close" aria-label="Close">✕</button>
        </div>

        <form className={styles.form} onSubmit={handleSubmit} id="ticket-form">
          {/* Product select */}
          <div className={styles.field}>
            <label className={styles.label}>Product</label>
            <select
              className={`${styles.select} input`}
              value={form.product}
              onChange={(e) => update("product", e.target.value)}
              id="ticket-product"
            >
              {Object.entries(PRODUCT_LABELS).filter(([k]) => k !== "unknown").map(([val, label]) => (
                <option key={val} value={val}>{label}</option>
              ))}
            </select>
          </div>

          {/* Name */}
          <div className={styles.field}>
            <label className={styles.label}>Full Name</label>
            <input
              type="text"
              className="input"
              placeholder="e.g. Rahul Sharma"
              value={form.customer_name}
              onChange={(e) => update("customer_name", e.target.value)}
              id="ticket-name"
              autoComplete="name"
            />
          </div>

          {/* Phone */}
          <div className={styles.field}>
            <label className={styles.label}>Phone Number</label>
            <input
              type="tel"
              className="input"
              placeholder="e.g. 9876543210"
              value={form.phone_number}
              onChange={(e) => update("phone_number", e.target.value)}
              id="ticket-phone"
              autoComplete="tel"
              maxLength={15}
            />
          </div>

          {/* Issue */}
          <div className={styles.field}>
            <label className={styles.label}>Issue Description</label>
            <textarea
              className={`${styles.textarea} input`}
              placeholder="Describe the problem in detail…"
              value={form.issue_description}
              onChange={(e) => update("issue_description", e.target.value)}
              id="ticket-issue"
              rows={3}
            />
          </div>

          {error && <p className={styles.errorMsg}>⚠️ {error}</p>}

          <div className={styles.actions}>
            <button type="button" className="btn btn-ghost" onClick={onClose} id="ticket-cancel">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading} id="ticket-submit">
              {loading ? <span className={styles.btnSpinner} /> : null}
              {loading ? "Submitting…" : "Submit Ticket"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

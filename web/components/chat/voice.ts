'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import type { Lang } from './chat-i18n'

type RecognitionEvent = { resultIndex: number; results: ArrayLike<ArrayLike<{ transcript: string }> & { isFinal: boolean }> }
type Recognition = {
  lang: string; interimResults: boolean; continuous: boolean
  onresult: ((event: RecognitionEvent) => void) | null
  onend: (() => void) | null
  onerror: (() => void) | null
  start: () => void; stop: () => void; abort: () => void
}
type RecognitionCtor = new () => Recognition

const LOCALE: Record<Lang, string> = { vi: 'vi-VN', en: 'en-US' }

function recognitionCtor(): RecognitionCtor | null {
  if (typeof window === 'undefined') return null
  const w = window as unknown as { SpeechRecognition?: RecognitionCtor; webkitSpeechRecognition?: RecognitionCtor }
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null
}

/** Dictation into the composer. `supported` is false where the Web Speech API is missing (e.g. Firefox). */
export function useDictation(lang: Lang, base: string, onText: (text: string) => void) {
  const [listening, setListening] = useState(false)
  const [supported, setSupported] = useState(false)
  const ref = useRef<Recognition | null>(null)
  useEffect(() => setSupported(recognitionCtor() !== null), [])
  useEffect(() => () => ref.current?.abort(), [])

  const stop = useCallback(() => ref.current?.stop(), [])
  const start = useCallback(() => {
    const Ctor = recognitionCtor()
    if (!Ctor || ref.current) return
    const recognition = new Ctor()
    recognition.lang = LOCALE[lang]
    recognition.interimResults = true
    recognition.continuous = false
    const prefix = base && !/\s$/.test(base) ? `${base} ` : base
    recognition.onresult = (event) => {
      let text = ''
      for (let i = 0; i < event.results.length; i++) text += event.results[i][0].transcript
      onText(prefix + text)
    }
    const finish = () => { ref.current = null; setListening(false) }
    recognition.onend = finish
    recognition.onerror = finish
    ref.current = recognition
    setListening(true)
    recognition.start()
  }, [lang, base, onText])

  return { supported, listening, toggle: () => (listening ? stop() : start()) }
}

/** Strip Markdown and [n] citation markers so text-to-speech reads naturally. */
export function plainText(markdown: string): string {
  return markdown
    .replace(/\[\d+\]/g, '')
    .replace(/[*_`#>|]/g, '')
    .replace(/^\s*[-•]\s+/gm, '')
    .replace(/\n{2,}/g, '. ')
    .replace(/\s+/g, ' ')
    .trim()
}

/** Read an answer aloud; `speaking` follows the message id so only one plays at a time. */
export function useSpeech(lang: Lang) {
  const [speakingId, setSpeakingId] = useState<string | null>(null)
  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window
  useEffect(() => () => { if (typeof window !== 'undefined' && 'speechSynthesis' in window) window.speechSynthesis.cancel() }, [])

  const toggle = useCallback((id: string, text: string, answerLang?: string) => {
    if (!('speechSynthesis' in window)) return
    const synth = window.speechSynthesis
    if (speakingId === id) { synth.cancel(); setSpeakingId(null); return }
    synth.cancel()
    const utterance = new SpeechSynthesisUtterance(plainText(text))
    utterance.lang = LOCALE[(answerLang as Lang) ?? lang] ?? LOCALE[lang]
    const voice = synth.getVoices().find((item) => item.lang.toLowerCase().startsWith(utterance.lang.slice(0, 2)))
    if (voice) utterance.voice = voice
    utterance.onend = utterance.onerror = () => setSpeakingId((current) => (current === id ? null : current))
    setSpeakingId(id)
    synth.speak(utterance)
  }, [lang, speakingId])

  return { supported, speakingId, toggle }
}

export const MAX_ATTACHMENT_BYTES = 4 * 1024 * 1024
export const ATTACHMENT_TYPES = ['image/png', 'image/jpeg', 'image/webp', 'application/pdf']

export type PendingAttachment = { name: string; mime: string; data: string }

/** Read a File into the base64 payload the API expects. */
export function readAttachment(file: File): Promise<PendingAttachment> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('read failed'))
    reader.onload = () => resolve({ name: file.name, mime: file.type, data: String(reader.result).split(',')[1] ?? '' })
    reader.readAsDataURL(file)
  })
}

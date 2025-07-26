import { Injectable, NgZone } from '@angular/core';

declare var webkitSpeechRecognition: any; // Chrome
declare var SpeechRecognition: any; // Other browsers

@Injectable({
  providedIn: 'root',
})
export class VoiceService {
  recognition: any;
  isListening: boolean = false;

  constructor(private zone: NgZone) {
    const SpeechRecognitionConstructor =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognitionConstructor) {
      throw new Error('Speech Recognition API is not supported in this browser.');
    }

    this.recognition = new SpeechRecognitionConstructor();
    this.recognition.lang = 'en-US'; // Set the desired language
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
  }

  startListening(onResult: (text: string) => void): void {
    this.isListening = true;
    this.recognition.start();

    this.recognition.onresult = (event: any) => {
      const text = event.results[0][0].transcript;
      this.zone.run(() => {
        onResult(text);
      });
    };

    this.recognition.onerror = (error: any) => {
      console.error('Speech recognition error:', error);
      this.isListening = false;
    };

    this.recognition.onend = () => {
      this.isListening = false;
    };
  }

  stopListening(): void {
    this.isListening = false;
    this.recognition.stop();
  }
}
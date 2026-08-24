import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

declare function gtag(cmd: string, id: string, params?: Record<string, any>): void;

@Component({
  selector: 'app-cookie-banner',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './cookie-banner.component.html',
  styleUrls: ['./cookie-banner.component.css']
})
export class CookieBannerComponent implements OnInit {
  visible = false;
  private readonly GA_ID = 'G-LNK1XETKNV';
  private readonly STORAGE_KEY = 'cr_cookie_consent';

  ngOnInit(): void {
    const consent = localStorage.getItem(this.STORAGE_KEY);
    if (!consent) {
      this.visible = true;
    } else if (consent === 'accepted') {
      this.enableGA();
    }
  }

  accept(): void {
    localStorage.setItem(this.STORAGE_KEY, 'accepted');
    this.visible = false;
    this.enableGA();
  }

  refuse(): void {
    localStorage.setItem(this.STORAGE_KEY, 'refused');
    this.visible = false;
    // GA reste désactivé
  }

  private enableGA(): void {
    // Charger le script GA dynamiquement
    if (!(window as any)['gaLoaded']) {
      (window as any)['ga-disable-' + this.GA_ID] = false;
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${this.GA_ID}`;
      document.head.appendChild(script);
      script.onload = () => {
        gtag('js', new Date().toString());
        gtag('config', this.GA_ID, { send_page_view: true });
        // Événements GA obligatoires (guide projet)
        this.setupGAEvents();
      };
      (window as any)['gaLoaded'] = true;
    }
  }

  private setupGAEvents(): void {
    // Événement : vue d'une page événement
    document.addEventListener('cr:event_view', (e: any) => {
      gtag('event', 'page_view_event', { event_id: e.detail?.id });
    });
    // Événement : soumission formulaire contact
    document.addEventListener('cr:form_submit', () => {
      gtag('event', 'form_submit', { form_name: 'contact' });
    });
    // Événement : clic CTA "En savoir plus"
    document.addEventListener('cr:cta_click', (e: any) => {
      gtag('event', 'cta_click', { cta_label: e.detail?.label });
    });
    // Événement : participation / réservation créneau
    document.addEventListener('cr:participation', (e: any) => {
      gtag('event', 'add_to_agenda', { event_id: e.detail?.id });
    });
  }
}

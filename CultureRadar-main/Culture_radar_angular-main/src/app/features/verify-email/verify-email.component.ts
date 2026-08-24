// src/app/features/verify-email/verify-email.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  standalone: true,
  selector: 'app-verify-email',
  imports: [CommonModule, HttpClientModule], // 👈 important pour *ngIf et HttpClient
  template: `
  <section class="verify-wrap">
    <h2>Vérification de l'e-mail</h2>

    <p *ngIf="state==='loading'">Validation en cours…</p>
    <p class="ok" *ngIf="state==='ok'">✅ Adresse vérifiée ! Tu peux te connecter.</p>
    <p class="err" *ngIf="state==='err'">{{ error || 'Lien invalide ou expiré.' }}</p>

    <button *ngIf="state!=='loading'" (click)="goLogin()">Aller à la connexion</button>
  </section>
  `,
  styles: [`.verify-wrap{max-width:680px;margin:40px auto;text-align:center}
            .ok{color:#059669}.err{color:#dc2626}`]
})
export class VerifyEmailComponent implements OnInit {
  state: 'loading'|'ok'|'err' = 'loading';
  error = '';
  API_BASE = environment.apiUrl;

  constructor(private ar: ActivatedRoute, private http: HttpClient, private router: Router){}

  ngOnInit(){
    const token = this.ar.snapshot.queryParamMap.get('token');
    if(!token){ this.state='err'; this.error='Token manquant'; return; }
    this.http.get(`${this.API_BASE}/auth/verify-email`, { params: { token } })
      .subscribe({
        next: () => this.state='ok',
        error: (e) => { this.state='err'; this.error = e?.error?.detail || ''; }
      });
  }
  goLogin(){ this.router.navigate(['/login']); }
}


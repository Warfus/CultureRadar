import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

/**
 * Formulaire d'inscription réservé aux organisateurs d'événements.
 * On ne leur demande pas leurs goûts ni leurs disponibilités (formulaire grand public),
 * mais les informations de leur structure : nom, type, SIRET, adresse, contact, programmation.
 */
@Component({
  selector: 'app-inscription-organisateur',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './inscription-organisateur.component.html',
  styleUrls: ['./inscription-organisateur.component.css'],
})
export class InscriptionOrganisateurComponent {
  private API_BASE = environment.apiUrl;

  referent = { nom: '', fonction: '', email: '', telephone: '', mot_de_passe: '' };
  structure = {
    nom_structure: '',
    type_structure: '',
    siret: '',
    site_web: '',
    adresse: '',
    code_postal: '',
    commune: '',
    frequence: '',
    description: '',
  };
  categoriesChoisies: string[] = [];
  accepteCgu = false;

  submitted = false;
  loading = false;
  showPassword = false;
  emailExists = false;
  serverError = '';

  typesStructure = [
    { value: 'salle', label: 'Salle ou lieu culturel' },
    { value: 'association', label: 'Association' },
    { value: 'collectif', label: "Collectif d'artistes" },
    { value: 'festival', label: 'Festival' },
    { value: 'collectivite', label: 'Collectivité, médiathèque, musée public' },
    { value: 'autre', label: 'Autre' },
  ];
  categories = [
    { value: 'concert', label: 'Concerts' },
    { value: 'exposition', label: 'Expositions' },
    { value: 'theatre', label: 'Théâtre et spectacles' },
    { value: 'atelier', label: 'Ateliers' },
    { value: 'famille', label: 'Sorties en famille' },
    { value: 'conference', label: 'Conférences et visites' },
  ];
  frequences = ['Moins de 1 par mois', '1 à 4 par mois', '5 à 10 par mois', 'Plus de 10 par mois'];

  constructor(private http: HttpClient, private router: Router) {}

  toggleCategorie(value: string, checked: boolean): void {
    const set = new Set(this.categoriesChoisies);
    checked ? set.add(value) : set.delete(value);
    this.categoriesChoisies = Array.from(set);
  }

  get emailOk(): boolean { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.referent.email.trim()); }
  get passwordOk(): boolean { return this.referent.mot_de_passe.length >= 8 && /[A-Z]/.test(this.referent.mot_de_passe); }
  get siretOk(): boolean { const s = this.structure.siret.replace(/\s/g, ''); return s === '' || /^\d{14}$/.test(s); }
  get cpOk(): boolean { return /^\d{5}$/.test(this.structure.code_postal.trim()); }

  get valid(): boolean {
    return this.referent.nom.trim().length > 0 && this.emailOk && this.passwordOk
      && this.structure.nom_structure.trim().length >= 2 && !!this.structure.type_structure
      && this.siretOk && this.cpOk && this.structure.commune.trim().length > 0
      && this.categoriesChoisies.length > 0 && this.accepteCgu;
  }

  onSubmit(): void {
    this.submitted = true;
    this.emailExists = false;
    this.serverError = '';
    if (!this.valid) return;

    const opt = (v: string) => (v.trim() ? v.trim() : null);
    const payload = {
      nom: this.referent.nom.trim(),
      email: this.referent.email.trim().toLowerCase(),
      mot_de_passe: this.referent.mot_de_passe,
      structure: {
        nom_structure: this.structure.nom_structure.trim(),
        type_structure: this.structure.type_structure,
        siret: opt(this.structure.siret.replace(/\s/g, '')),
        fonction_referent: opt(this.referent.fonction),
        telephone: opt(this.referent.telephone),
        site_web: opt(this.structure.site_web),
        adresse: opt(this.structure.adresse),
        code_postal: this.structure.code_postal.trim(),
        commune: this.structure.commune.trim(),
        categories: this.categoriesChoisies,
        frequence: opt(this.structure.frequence),
        description: opt(this.structure.description),
      },
    };

    this.loading = true;
    this.http.post(`${this.API_BASE}/utilisateurs/organisateurs`, payload).subscribe({
      next: () => {
        this.loading = false;
        alert('Compte organisateur créé ✅ Connectez-vous pour publier votre premier événement.');
        this.router.navigate(['/login']);
      },
      error: err => {
        this.loading = false;
        if (err.status === 409) { this.emailExists = true; return; }
        const d = err?.error?.detail;
        this.serverError = typeof d === 'string' ? d : 'Une erreur est survenue, merci de vérifier les champs.';
      },
    });
  }
}

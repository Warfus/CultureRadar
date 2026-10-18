import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-devenir-organisateur',
  imports: [CommonModule, RouterModule],
  template: `
  <section class="hero" aria-labelledby="orga-h1">
    <h1 id="orga-h1">Faites découvrir vos événements aux bonnes personnes</h1>
    <p class="lead">Salles indépendantes, associations, collectifs, festivals, médiathèques : publiez gratuitement vos événements
      sur CultureRadar et nous les recommandons aux habitants qu'ils peuvent vraiment intéresser, selon leurs goûts, leur quartier et leurs disponibilités.</p>
    <div class="cta-row">
      <a routerLink="/register" class="btn primary">Créer mon compte organisateur</a>
      <a href="#offres" class="btn ghost">Voir les offres</a>
    </div>
  </section>

  <div class="container">
    <section aria-labelledby="concept-h2">
      <h2 id="concept-h2">Le concept : une recommandation, pas un catalogue</h2>
      <p>Sur les agendas classiques, votre concert se perd au milieu de milliers d'annonces. CultureRadar fonctionne autrement :
        chaque utilisateur indique ce qu'il aime, où il habite et quand il est disponible. Notre moteur lui propose alors les sorties
        qui lui correspondent, y compris celles des petits lieux qu'il ne connaissait pas. Votre événement est mis devant un public
        qui a envie de le voir.</p>
      <ul class="figures" aria-label="Chiffres clés">
        <li><strong>20-45 ans</strong><span>le public principal de la plateforme</span></li>
        <li><strong>0 €</strong><span>pour publier vos événements</span></li>
        <li><strong>5 minutes</strong><span>pour créer votre premier événement</span></li>
      </ul>
    </section>

    <section aria-labelledby="avantages-h2">
      <h2 id="avantages-h2">Pourquoi publier sur CultureRadar ?</h2>
      <div class="grid">
        <article class="card">
          <h3>Remplissez votre salle</h3>
          <p>Vos événements apparaissent dans les recommandations des personnes intéressées par votre programmation et proches de chez vous.</p>
        </article>
        <article class="card">
          <h3>Gagnez du temps</h3>
          <p>Un formulaire unique : titre, dates, lieu, prix, âge conseillé. Votre événement est en ligne immédiatement, sur ordinateur comme sur mobile.</p>
        </article>
        <article class="card">
          <h3>Suivez vos résultats</h3>
          <p>Votre tableau de bord affiche les vues, les réservations et les notes laissées par le public pour chaque événement.</p>
        </article>
      </div>
    </section>

    <section aria-labelledby="etapes-h2">
      <h2 id="etapes-h2">Comment ça marche ?</h2>
      <ol class="steps">
        <li><h3>Créez votre compte</h3><p>Inscrivez-vous avec l'adresse e-mail de votre structure, puis demandez l'accès organisateur depuis la page contact.</p></li>
        <li><h3>Publiez vos événements</h3><p>Depuis l'espace « Organiser », ajoutez vos événements et leurs séances en quelques clics.</p></li>
        <li><h3>Touchez un nouveau public</h3><p>Vos événements sont recommandés, réservés et notés : vous voyez l'effet en temps réel.</p></li>
      </ol>
    </section>

    <section id="offres" aria-labelledby="offres-h2">
      <h2 id="offres-h2">Nos offres</h2>
      <div class="grid">
        <article class="card offer">
          <h3>Gratuit</h3>
          <p class="price">0 €</p>
          <ul><li>Publication illimitée</li><li>Recommandation aux utilisateurs</li><li>Statistiques de base</li></ul>
        </article>
        <article class="card offer highlight">
          <h3>Mise en avant</h3>
          <p class="price">à partir de 29 € HT par événement</p>
          <ul><li>Événement placé en tête de l'accueil</li><li>Priorité dans les recommandations</li><li>Badge « Coup de cœur »</li></ul>
        </article>
        <article class="card offer">
          <h3>Partenaire</h3>
          <p class="price">sur devis</p>
          <ul><li>Pour les collectivités et réseaux de lieux</li><li>Page dédiée à votre territoire</li><li>Rapports d'audience mensuels</li></ul>
        </article>
      </div>
    </section>

    <section aria-labelledby="faq-h2">
      <h2 id="faq-h2">Questions fréquentes</h2>
      <details><summary>La publication est-elle vraiment gratuite ?</summary><p>Oui. Seule la mise en avant, facultative, est payante.</p></details>
      <details><summary>Quels types d'événements puis-je publier ?</summary><p>Concerts, expositions, spectacles, ateliers, festivals, visites, conférences : tout événement culturel ouvert au public.</p></details>
      <details><summary>Combien de temps pour activer mon espace ?</summary><p>Votre accès organisateur est activé sous 48 heures ouvrées après votre demande.</p></details>
    </section>

    <section class="final" aria-labelledby="final-h2">
      <h2 id="final-h2">Prêt à faire découvrir votre programmation ?</h2>
      <div class="cta-row">
        <a routerLink="/register" class="btn primary">Devenir organisateur</a>
        <a routerLink="/contact" class="btn ghost">Poser une question</a>
      </div>
      <p class="note">Projet étudiant fictif IAS B3 : aucune transaction réelle n'est effectuée.</p>
    </section>
  </div>
  `,
  styles: [`
    :host { display:block; font-family: 'Roboto', sans-serif; color:#1f1f1f; }
    h1, h2, h3 { font-family: 'Poppins', sans-serif; }
    .hero { background:#9e0047; color:#fff; text-align:center; padding:56px 20px; }
    .hero h1 { font-size: clamp(26px, 4vw, 40px); margin:0 0 12px; }
    .lead { max-width: 760px; margin: 0 auto 20px; font-size:18px; line-height:1.5; }
    .container { max-width: 1100px; margin: 0 auto; padding: 24px 16px 48px; }
    section { margin: 36px 0; }
    h2 { color:#9e0047; font-size: 26px; margin: 0 0 14px; }
    h3 { font-size: 19px; margin: 0 0 8px; }
    .figures { list-style:none; padding:0; display:grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap:16px; }
    .figures li { background:#fde4b1; border-radius:14px; padding:16px; text-align:center; }
    .figures strong { display:block; font-size:28px; color:#9e0047; }
    .grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(260px,1fr)); gap:20px; }
    .card { background:#fff; border:1px solid #e5e5e5; border-radius:16px; padding:20px; box-shadow:0 4px 12px rgba(0,0,0,.05); }
    .offer.highlight { border:2px solid #D72670; }
    .price { font-weight:700; color:#9e0047; font-size:18px; }
    .steps { padding-left: 22px; }
    .steps li { margin-bottom: 14px; }
    details { border-bottom:1px solid #ddd; padding:12px 0; }
    summary { cursor:pointer; font-weight:600; }
    .cta-row { display:flex; gap:12px; justify-content:center; flex-wrap:wrap; }
    .btn { display:inline-block; padding:12px 22px; border-radius:24px; font-weight:700; text-decoration:none; font-family:'Poppins',sans-serif; }
    .btn.primary { background:#fff; color:#9e0047; }
    .final .btn.primary, .container .btn.primary { background:#D72670; color:#fff; }
    .btn.ghost { border:2px solid currentColor; color:inherit; }
    .btn:focus-visible, summary:focus-visible { outline:3px solid #049eb3; outline-offset:3px; }
    .final { text-align:center; background:#fff7e8; border-radius:16px; padding:32px 16px; }
    .note { font-size: 13px; color:#555; margin-top:14px; }
  `],
})
export class DevenirOrganisateurComponent {}

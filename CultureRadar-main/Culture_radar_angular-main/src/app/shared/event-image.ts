/**
 * Image par défaut d'un événement qui n'a pas d'image (événements de démonstration,
 * ou événements OpenAgenda sans visuel) : on choisit une illustration selon la catégorie,
 * déduite des mots-clés puis du titre. Les illustrations sont dans public/assets/evenements/.
 */
const REGLES: Array<[RegExp, string]> = [
  [/jazz/, 'jazz'],
  [/\brap\b|hip.?hop|slam/, 'rap'],
  [/classique|orchestre|op[ée]ra|symphon/, 'classique'],
  [/danse|bal\b|folk/, 'bal-folk'],
  [/street.?art|art urbain|graff/, 'street-art'],
  [/atelier.*artiste|visite/, 'ateliers-artistes'],
  [/\bbd\b|bande dessin[ée]e|atelier/, 'atelier-enfants'],
  [/conte|jeune public|marionnette/, 'conte'],
  [/cin[ée]ma|film|projection|documentaire/, 'cinema'],
  [/th[ée][aâ]tre|humour|impro|com[ée]die|spectacle/, 'theatre'],
  [/expo/, 'ateliers-artistes'],
];

export function imageParDefaut(keywords?: string[] | null, titre?: string | null): string {
  const texte = `${(keywords || []).join(' ')} ${titre || ''}`.toLowerCase();
  for (const [re, nom] of REGLES) {
    if (re.test(texte)) return `/assets/evenements/${nom}.jpg`;
  }
  return '/assets/Concert.jpg';
}

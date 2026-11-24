import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService } from '../../shared/admin.service';

@Component({
  standalone: true,
  selector: 'app-dashboard-admin',
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard-admin.component.html',
  styleUrls: ['./dashboard-admin.component.css']
})
export class DashboardAdminComponent implements OnInit {
  // Overview
  loading = true; error = '';
  ov: any = null; series: any = null; top: any = null; quality: any = null;

  // Tabs
  tab: 'overview' | 'users' | 'events' = 'overview';

  // Users
  uLoading = false; uError = ''; uQ = ''; uPage = 1; uPer = 20; users: any[] = [];

  // Events
  eLoading = false; eError = ''; eQ = ''; ePage = 1; ePer = 20; events: any[] = [];

  constructor(private admin: AdminService) {}

  ngOnInit(): void {
    Promise.all([
      this.admin.overview().toPromise(),
      this.admin.series(30).toPromise(),
      this.admin.top().toPromise(),
      this.admin.quality().toPromise(),
    ]).then(([ov, s, t, q]) => {
      this.series = s;
      this.ov = this.mapOverview(ov, s, q);
      this.quality = this.mapQuality(q);
      this.top = this.mapTop(t);
      this.loading = false;
    }).catch(() => { this.error = 'Impossible de charger le dashboard.'; this.loading = false; });
  }

  // Tabs
  setTab(t: 'overview' | 'users' | 'events') {
    this.tab = t;
    if (t === 'users' && !this.users.length) this.loadUsers();
    if (t === 'events' && !this.events.length) this.loadEvents();
  }

  // Adapte les réponses de l'API (total_users, premium_users...) aux noms utilisés par la page
  private sumLastDays(series: any, key: string, days = 7): number {
    const rows: any[] = series?.series || [];
    return rows.slice(-days).reduce((acc, r) => acc + (r?.[key] || 0), 0);
  }
  private mapOverview(ov: any, series: any, q: any) {
    if (!ov) return null;
    const total = q?.total_events ?? ov.total_events ?? 0;
    const withImage = total ? ((total - (q?.missing_image ?? 0)) / total) * 100 : 0;
    return {
      users_total: ov.total_users ?? 0,
      users_new_7d: this.sumLastDays(series, 'signups'),
      organizers: ov.organizers ?? 0,
      premium_active: ov.premium_users ?? 0,
      events_total: ov.total_events ?? 0,
      events_upcoming: ov.upcoming_events ?? 0,
      participations_total: ov.total_participations ?? 0,
      participations_7d: this.sumLastDays(series, 'participations'),
      rating_avg_global: ov.average_rating,
      ratings_count: ov.total_ratings ?? 0,
      events_with_image_pct: withImage,
    };
  }
  private mapQuality(q: any) {
    if (!q) return null;
    return {
      missing_image: q.missing_image ?? 0,
      missing_description: q.missing_description ?? 0,
      missing_occurrences: q.without_occurrence ?? 0,
    };
  }
  private mapTop(t: any) {
    const rows: any[] = Array.isArray(t) ? t : [];
    const toItem = (r: any, metric: number) => ({ titre: r.titre, commune: r.commune, image_url: null, metric });
    return {
      most_participated: rows.filter(r => (r.participations_count || 0) > 0)
        .map(r => toItem(r, r.participations_count)),
      best_rated: rows.filter(r => r.average_rating != null)
        .sort((a, b) => b.average_rating - a.average_rating)
        .map(r => toItem(r, r.average_rating)),
    };
  }

  // Helpers
  pct(v:number){ return (v ?? 0).toFixed(1) + '%'; }
  barW(n:number, max:number){ const w = max ? Math.round((n/max)*100) : 0; return {width: w + '%'}; }

  // Users
  loadUsers() {
    this.uLoading = true; this.uError = '';
    this.admin.users(this.uPage, this.uPer, this.uQ).subscribe({
      next: (rows) => { this.users = rows || []; this.uLoading = false; },
      error: () => { this.uError = 'Chargement utilisateurs impossible'; this.uLoading = false; }
    });
  }
  uSearch() { this.uPage = 1; this.loadUsers(); }
  uPrev(){ if (this.uPage>1){ this.uPage--; this.loadUsers(); } }
  uNext(){ this.uPage++; this.loadUsers(); }
  deleteUser(id:number) {
    if (!confirm('Supprimer cet utilisateur ? Cette action est définitive.')) return;
    this.admin.deleteUser(id).subscribe({
      next: () => this.users = this.users.filter(u => u.id !== id),
      error: () => alert('Suppression impossible')
    });
  }

  // Events
  loadEvents() {
    this.eLoading = true; this.eError = '';
    this.admin.events(this.ePage, this.ePer, this.eQ).subscribe({
      next: (rows) => { this.events = rows || []; this.eLoading = false; },
      error: () => { this.eError = 'Chargement événements impossible'; this.eLoading = false; }
    });
  }
  eSearch() { this.ePage = 1; this.loadEvents(); }
  ePrev(){ if (this.ePage>1){ this.ePage--; this.loadEvents(); } }
  eNext(){ this.ePage++; this.loadEvents(); }
  deleteEvent(id:number) {
    if (!confirm('Supprimer cet événement ?')) return;
    this.admin.deleteEvent(id).subscribe({
      next: () => this.events = this.events.filter(e => e.id !== id),
      error: () => alert('Suppression impossible')
    });
  }

  downloadExport() {
    this.admin.exportZip().subscribe({
      next: (blob: Blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cultureradar_export.zip`;
        a.click();
        URL.revokeObjectURL(url);
      },
      error: () => alert('Export impossible pour le moment')
    });
  }
}


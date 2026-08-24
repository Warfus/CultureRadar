// src/app/shared/organizer.guard.ts
import { CanActivateFn, Router } from '@angular/router';
import { inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, map, of } from 'rxjs';
import { environment } from '../../environments/environment';

const API_BASE = environment.apiUrl;

export const organizerGuard: CanActivateFn = () => {
  const http = inject(HttpClient);
  const router = inject(Router);

  return http.get<any>(`${API_BASE}/utilisateurs/me`).pipe(
    map(me => {
      const ok = me?.role === 'organizer' || me?.is_organizer === true || me?.roles?.includes?.('organizer');
      if (ok) return true;
      router.navigateByUrl('/');
      return false;
    }),
    catchError(() => {
      router.navigateByUrl('/');
      return of(false);
    })
  );
};


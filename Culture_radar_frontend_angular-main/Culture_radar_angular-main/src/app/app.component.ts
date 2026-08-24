import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd, RouterModule } from '@angular/router';
import { NavbarComponent } from './shared/navbar/navbar.component';
import { FooterComponent } from './shared/footer/footer.component';
import { CookieBannerComponent } from './shared/cookie-banner/cookie-banner.component';
import { filter } from 'rxjs/operators';
import { CommonModule } from '@angular/common';
import { AuthService } from './shared/auth.service';

declare function gtag(cmd: string, event: string, params?: Record<string, any>): void;

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule, NavbarComponent, FooterComponent, CookieBannerComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  showNavbar = true;
  isLoggedIn = false;

  constructor(private router: Router, private authService: AuthService) {
    this.router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe((e: NavigationEnd) => {
        this.showNavbar = (e.urlAfterRedirects || e.url) !== '/';

        // GA4: page_view seulement si consentement donné
        try {
          const consent = localStorage.getItem('cr_cookie_consent');
          if (consent === 'accepted') {
            gtag('event', 'page_view', {
              page_path: e.urlAfterRedirects || e.url
            });
          }
        } catch {}
      });
  }

  ngOnInit(): void {
    this.authService.isLoggedIn$.subscribe(status => {
      this.isLoggedIn = status;
    });
  }

  logout(): void {
    this.authService.logout();
    this.isLoggedIn = false;
    this.router.navigate(['/']);
  }
}

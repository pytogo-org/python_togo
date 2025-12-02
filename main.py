"""
Python Togo FastAPI application.

This module defines a small FastAPI server that serves HTML templates,
static assets, and a few JSON API endpoints for events, news, communities,
and basic forms (join, contact, partnership).

Notes
-----
- Translations are stored in-memory in `TRANSLATIONS` and selected via
    cookie or `Accept-Language`.
- Sample data for events and news is kept in-memory for simplicity.
"""

import os
import json
from datetime import date
from typing import List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError

app = FastAPI(title="Python Togo")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
load_dotenv()
SUBABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUBABASE_URL, SUPABASE_KEY)

# Simple in-memory sample data
SAMPLE_EVENTS = [
    {
        "id": 1,
        "date": "2025-12-05",
        "location": "Lomé",
        "translations": {
            "fr": {
                "title": "Atelier Python débutant",
                "description": "Introduction à Python pour les nouveaux développeurs.",
            },
            "en": {
                "title": "Beginner Python workshop",
                "description": "Introduction to Python for new developers.",
            },
        },
    },
    {
        "id": 3,
        "date": "2025-07-20  to 2025-08-22",
        "location": "Lomé",
        "translations": {
            "fr": {
                "title": "Challenge 30 jours de code Python",
                "description": (
                    "Challenge d'introduction à Python pour les nouveaux développeurs."
                ),
            },
            "en": {
                "title": "30 Days of Python Code Challenge",
                "description": "Introductory Python challenge for new developers.",
            },
        },
    },
    {
        "id": 2,
        "date": "2026-01-20",
        "location": "Lomé",
        "translations": {
            "fr": {
                "title": "Data Science avec Python",
                "description": "Atelier sur les bases de la data science.",
            },
            "en": {
                "title": "Data Science with Python",
                "description": "Workshop on the basics of data science.",
            },
        },
    },
]

SAMPLE_NEWS = [
    {
        "id": 1,
        "date": "2025-11-01",
        "image": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1763440928/20251117_200618_tsfc73.jpg",
        "translations": {
            "fr": {
                "title": "Lancement d'un nouvel atelier Python",
                "excerpt": "Nous organisons un atelier sur les bases de Python.",
                "body": (
                    "Rejoignez-nous pour un atelier d'introduction à Python, destiné "
                    "aux débutants. Détails, date et inscription seront "
                    "communiqués prochainement."
                ),
            },
            "en": {
                "title": "Launching a new Python workshop",
                "excerpt": "We are organizing a beginner-friendly Python workshop.",
                "body": (
                    "Join us for an introductory Python workshop for newcomers. "
                    "Details, date, and registration will be shared soon."
                ),
            },
        },
    },
    {
        "id": 2,
        "date": "2025-09-15",
        "image": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1763440928/20251117_200618_tsfc73.jpg",
        "translations": {
            "fr": {
                "title": "Rencontre communautaire à Lomé",
                "excerpt": "Retour sur la rencontre mensuelle.",
                "body": (
                    "Compte-rendu de notre dernière rencontre communautaire à Lomé "
                    "avec les ressources partagées et les annonces."
                ),
            },
            "en": {
                "title": "Community meetup in Lomé",
                "excerpt": "Recap of the monthly meetup.",
                "body": (
                    "A recap of our latest community meetup in Lomé with shared "
                    "resources and announcements."
                ),
            },
        },
    },
    {
        "id": 3,
        "date": "2025-08-23",
        "image": "https://res.cloudinary.com/dvg7vky5o/image/upload/v1747588996/Group_6_r7n6id.png",
        "translations": {
            "fr": {
                "title": "Rapport de la PyCon Togo 2025",
                "excerpt": "Retour sur la PyCon Togo 2025.",
                "body": (
                    "Compte-rendu de la PyCon Togo 2025 avec les ressources "
                    "partagées et les annonces. "
                    "lire plus: https://report.pytogo.org/rapport-de-la-pycon-togo-2025"
                ),
            },
            "en": {
                "title": "PyCon Togo 2025 Report",
                "excerpt": "Recap of the PyCon Togo 2025.",
                "body": (
                    "A recap of the PyCon Togo 2025 with shared resources and "
                    "announcements. "
                    "read more: https://report.pytogo.org"
                ),
            },
        },
    },
]


TRANSLATIONS = {
    "fr": {
        "site-title": "Python Togo",
        "nav-home": "Accueil",
        "nav-about": "À propos",
        "nav-code": "Code de conduite",
        "nav-events": "Événements",
        "nav-news": "Actualités",
        "nav-gallery": "Galerie",
        "nav-join": "Adhérer",
        "nav-contact": "Contact",
        "nav-partners": "Partenaires",
        "nav-communities": "Communautés",
        "lang-fr": "FR",
        "lang-en": "EN",
        "donate": "Faire un don",
        "footer-about-title": "À propos",
        "footer-about-desc": (
            "Python Togo promeut le langage de programmation Python au Togo."
        ),
        "footer-links-title": "Liens",
        "footer-contact-title": "Contact",
        "footer-logo-by": "Logo conçu avec ❤️ par",
        "footer-site-by": "Ce site a été conçu et développé avec ❤️ par",
        "footer-using": "à l'aide de",
        "footer-and-deployed": "et déployé sur",
        "footer-rights": "Tous droits réservés.",
        "footer-logos": "Logos",
        "gallery-title": "Galerie",
        "gallery-intro": (
            "Découvrez les photos de nos événements et rencontres. Cliquez sur le "
            "lien ci-dessous pour accéder à notre album."
        ),
        "gallery-view": "Voir",
        "gallery-external": "Voir notre galerie",
        "gallery-external-coming": "Voir notre galerie (à venir)",
        "gallery-recent": "Vignettes récentes",
        "join-title": "Adhérer",
        "join-intro": (
            "Rejoignez la communauté Python Togo en remplissant le formulaire "
            "ci-dessous."
        ),
        "label-name": "Nom",
        "label-fullname": "Nom complet",
        "label-email": "Email",
        "label-city": "Ville",
        "label-level": "Niveau Python",
        "level-beginner": "Débutant",
        "level-intermediate": "Intermédiaire",
        "level-advanced": "Avancé",
        "btn-send": "Envoyer",
        "contact-title": "Contact",
        "contact-intro": (
            "Pour toute question, envoyez-nous un message via le formulaire."
        ),
        "label-subject": "Sujet",
        "label-message": "Message",
        "agree-privacy": "J'ai lu et j'accepte la politique de confidentialité",
        "agree-coc": "J'ai lu et j'accepte le Code de conduite",
        "consent-alert": (
            "Veuillez accepter la politique de confidentialité et le Code de "
            "conduite avant de continuer."
        ),
        "privacy-link-text": "Politique de confidentialité",
        "news-title": "Actualités",
        "news-read-more": "Voir plus",
        "news-back": "Retour aux actualités",
        "privacy-title": "Politique de confidentialité",
        "privacy-heading": "Politique de confidentialité",
        "privacy-intro": (
            "Chez Python Togo, nous prenons la confidentialité de vos données au "
            "sérieux. Cette page explique quelles données nous collectons, "
            "pourquoi nous les collectons et comment nous les utilisons."
        ),
        "privacy-collect-heading": "Données que nous collectons",
        "privacy-collect-1": (
            "Données de contact : nom, adresse e‑mail, téléphone (si fournies) "
            "lorsque vous remplissez un formulaire."
        ),
        "privacy-collect-2": (
            "Informations de profil : ville, niveau, intérêts (quand vous les "
            "partagez)."
        ),
        "privacy-collect-3": (
            "Données techniques : adresse IP, type de navigateur et timing des "
            "requêtes pour améliorer nos services."
        ),
        "privacy-why-heading": "Pourquoi nous collectons ces données",
        "privacy-why-intro": "Nous utilisons vos données pour :",
        "privacy-why-1": "Répondre à vos demandes (adhésion, partenariat, contact).",
        "privacy-why-2": "Organiser et informer sur les événements.",
        "privacy-why-3": "Améliorer l'expérience et la sécurité du site.",
        "privacy-share-heading": "Partage et conservation",
        "privacy-share-text": (
            "Nous ne vendons ni ne louons vos données personnelles. Les demandes "
            "reçues peuvent être partagées avec les membres organisateurs et "
            "conservées aussi longtemps que nécessaire pour répondre à la "
            "demande ou se conformer aux obligations légales."
        ),
        "privacy-retention-sub": "Durée de conservation",
        "privacy-retention-intro": (
            "Nous conservons vos données aussi longtemps que nécessaire pour "
            "atteindre les objectifs pour lesquels elles ont été collectées. "
            "Par exemple :"
        ),
        "privacy-retention-1": (
            "Demandes d'adhésion : conservées pendant 3 ans après la dernière "
            "interaction, sauf si vous demandez leur suppression."
        ),
        "privacy-retention-2": (
            "Inscriptions à des événements : conservées pendant la durée "
            "nécessaire à l'organisation et archivées pendant 3 ans pour des "
            "raisons administratives."
        ),
        "privacy-retention-3": (
            "Messages de contact : conservés pendant 2 à 3 ans selon la nature "
            "de la demande."
        ),
        "privacy-disclosure-sub": "Partage et divulgation",
        "privacy-disclosure-text": (
            "Nous ne partageons pas vos données personnelles avec des tiers à des "
            "fins commerciales sans votre consentement explicite. Les données "
            "peuvent être partagées avec des prestataires qui traitent les "
            "données pour notre compte (hébergement, envoi d'emails), sous "
            "contrat de confidentialité."
        ),
        "privacy-rights-heading": "Vos droits",
        "privacy-rights-text": (
            "Vous pouvez demander l'accès, la rectification ou la suppression de "
            "vos données en nous contactant à"
        ),
        "privacy-forms-heading": "Formulaires et consentement",
        "privacy-forms-intro": (
            "Tous les formulaires importants (adhésion, partenariat) exigent votre "
            "consentement explicite :"
        ),
        "privacy-forms-privacy": (
            "Vous devez cocher la case indiquant que vous avez lu et accepté "
            "notre politique de confidentialité."
        ),
        "privacy-forms-coc": (
            "Vous devez cocher la case indiquant que vous acceptez le Code de "
            "conduite de la communauté."
        ),
        "privacy-questions": (
            "Si vous avez des questions sur cette politique, contactez-nous à"
        ),
        "coc-title": "Code de conduite",
        "coc-heading": "Code de conduite",
        "coc-intro": (
            "Cette charte s'inspire des meilleures pratiques utilisées par les "
            "communautés Python, notamment celles de la Python Software "
            "Foundation (PSF). Elle vise à garantir un environnement sûr, "
            "accueillant et professionnel pour toutes et tous, quelles que "
            "soient l'expérience, l'identité ou l'origine."
        ),
        "coc-commitment": "Notre engagement",
        "coc-commitment-intro": "Nous nous engageons à :",
        "coc-commitment-1": (
            "Fournir un espace inclusif et respectueux pour les événements, "
            "forums et canaux en ligne liés à Python Togo."
        ),
        "coc-commitment-2": "Valoriser la diversité des parcours et des contributions.",
        "coc-commitment-3": (
            "Répondre rapidement et de manière confidentielle aux signalements "
            "de comportements inappropriés."
        ),
        "coc-expected": "Comportements attendus",
        "coc-expected-1": "Respecter les autres participants et leurs opinions.",
        "coc-expected-2": (
            "Être attentif(ve) au langage employé et utiliser un ton constructif."
        ),
        "coc-expected-3": (
            "Accepter les retours avec humilité et être prêt(e) à s'excuser en "
            "cas d'erreur."
        ),
        "coc-expected-4": (
            "Respecter les règles spécifiques aux lieux ou aux plateformes "
            "(modération, sécurité, accessibilité)."
        ),
        "coc-unacceptable": "Comportements inacceptables",
        "coc-unacceptable-intro": "Ne seront pas tolérés :",
        "coc-unacceptable-1": (
            "Les propos discriminatoires, le harcèlement, les attaques "
            "personnelles ou menaces."
        ),
        "coc-unacceptable-2": (
            "La diffusion d'insultes, propos sexistes, racistes, homophobes, "
            "transphobes ou tout autre contenu haineux."
        ),
        "coc-unacceptable-3": (
            "Le partage non consenti d'informations personnelles ou confidentielles."
        ),
        "coc-unacceptable-4": (
            "Le non-respect des consignes de sécurité et de modération des "
            "organisateurs."
        ),
        "coc-scope": "Périmètre",
        "coc-scope-text": (
            "Ce code s'applique à tous les espaces officiels et événements "
            "organisés par Python Togo, y compris les réunions en présentiel, "
            "ateliers, conférences, listes de diffusion, forums et canaux de "
            "discussion en ligne associés."
        ),
        "coc-report": "Procédure de signalement",
        "coc-report-intro": (
            "Si vous êtes victime ou témoin d'un comportement inacceptable :"
        ),
        "coc-report-1": (
            "Contactez d'abord les organisateurs via la page de contact ou "
            "envoyez un email à"
        ),
        "coc-report-2": (
            "Fournissez autant de détails que possible : date, lieu, personnes "
            "impliquées, témoins et copies de messages si pertinent."
        ),
        "coc-report-3": (
            "Indiquez si vous souhaitez que votre signalement soit traité de "
            "façon confidentielle."
        ),
        "coc-handling": "Gestion des signalements",
        "coc-handling-text": (
            "Les organisateurs examineront les signalements rapidement et "
            "prendront des mesures proportionnées, qui peuvent inclure :"
        ),
        "coc-handling-1": "Un avertissement formel.",
        "coc-handling-2": "La suspension ou exclusion d'un événement ou d'un canal.",
        "coc-handling-3": (
            "La communication d'informations aux autorités compétentes si nécessaire."
        ),
        "coc-confidentiality": "Confidentialité et protection",
        "coc-confidentiality-text": (
            "Les informations reçues dans le cadre d'un signalement seront "
            "traitées avec la plus grande confidentialité possible. Seules les "
            "personnes nécessaires à l'enquête auront accès aux informations."
        ),
        "coc-examples": "Exemples",
        "coc-examples-intro": "Exemples de comportements à signaler :",
        "coc-examples-1": (
            "Messages répétés et non sollicités d'un individu visant une autre "
            "personne."
        ),
        "coc-examples-2": (
            "Commentaires à caractère discriminatoire sur la base d'une identité."
        ),
        "coc-examples-3": "Partage d'une photo privée sans consentement.",
        "coc-organizers": "Responsabilités des organisateurs",
        "coc-organizers-intro": "Les organisateurs s'engagent à :",
        "coc-organizers-1": (
            "Maintenir des procédures claires pour la gestion des incidents."
        ),
        "coc-organizers-2": (
            "Former, si nécessaire, les modérateurs et responsables à la "
            "gestion des signalements."
        ),
        "coc-organizers-3": (
            "Publier des mises à jour sur les mesures prises, sans compromettre "
            "la confidentialité."
        ),
        "coc-revision": "Révision",
        "coc-revision-text": (
            "Ce code de conduite pourra être revu périodiquement pour s'adapter "
            "aux retours de la communauté et aux bonnes pratiques "
            "internationales."
        ),
        "coc-thanks": (
            "Merci de contribuer à faire de Python Togo un espace sûr et "
            "accueillant pour tous."
        ),
        "home-title": "Accueil",
        "home-welcome": "Bienvenue sur Python Togo",
        "home-intro": (
            "Python Togo est une communauté de développeurs et passionnés Python "
            "au Togo. Nous organisons des événements, des formations et "
            "promouvons l'usage de Python dans notre pays."
        ),
        "home-join": "Rejoindre la communauté",
        "home-view-events": "Voir les événements",
        "home-news-recent": "Actualités récentes",
        "home-news-all": "Voir toutes les actualités",
        "partners-our": "Nos partenaires",
        "partners-intro": (
            "Nous remercions les organisations et individus qui nous font confiance."
        ),
        "partners-none": "Aucun partenaire pour le moment.",
        "partners-request-title": "Demander un partenariat",
        "partners-request-intro": (
            "Vous souhaitez nous soutenir ou devenir partenaire ? "
            "Envoyez votre demande ci-dessous."
        ),
        "label-organization": "Organisation",
        "label-contact-name": "Nom du contact",
        "label-website-optional": "Site web (optionnel)",
        "label-message-optional": "Message (optionnel)",
        "partners-send": "Envoyer la demande",
        "partners-sending": "Envoi en cours...",
        "partners-success": "Demande envoyée, merci !",
        "partners-error-prefix": "Erreur: ",
        "partners-network-error-prefix": "Erreur réseau: ",
        "about-title": "À propos",
        "about-heading": "À propos",
        "about-blurb": (
            "Python Togo rassemble les développeurs, étudiants et professionnels "
            "utilisant Python au Togo. Notre mission est de promouvoir "
            "l'apprentissage et l'utilisation de Python."
        ),
        "about-mission": "Notre mission",
        "about-m1": "Promouvoir l'apprentissage et l'utilisation de Python",
        "about-m2": "Organiser des événements et formations",
        "about-m3": "Favoriser le partage de connaissances",
        "events-title": "Événements",
        "events-heading": "Événements",
        "events-sample-meta": "2025-12-05 • Lomé",
        "events-sample-title": "Atelier Python débutant",
        "events-sample-desc": "Introduction à Python pour les nouveaux développeurs.",
        "communities-title": "Communautés",
        "communities-heading": "Communautés locales",
        "communities-card-title": "Python Togo",
        "communities-card-desc": (
            "Groupe local basé à Lomé, rencontre mensuelle et ateliers."
        ),
    },
    "en": {
        "site-title": "Python Togo",
        "nav-home": "Home",
        "nav-about": "About",
        "nav-code": "Code of Conduct",
        "nav-events": "Events",
        "nav-news": "News",
        "nav-gallery": "Gallery",
        "nav-join": "Join",
        "nav-contact": "Contact",
        "nav-partners": "Partners",
        "nav-communities": "Communities",
        "lang-fr": "FR",
        "lang-en": "EN",
        "donate": "Donate",
        "footer-about-title": "About",
        "footer-about-desc": (
            "Python Togo promotes the Python programming language in Togo."
        ),
        "footer-links-title": "Links",
        "footer-contact-title": "Contact",
        "footer-logo-by": "Logo designed with ❤️ by",
        "footer-site-by": "This site was designed and developed with ❤️ by",
        "footer-using": "using",
        "footer-and-deployed": "and deployed on",
        "footer-rights": "All rights reserved.",
        "footer-logos": "Logos",
        "gallery-title": "Gallery",
        "gallery-intro": (
            "Discover photos from our events and meetups. Use the link below "
            "to access our album."
        ),
        "gallery-view": "View",
        "gallery-external": "View our gallery",
        "gallery-external-coming": "View our gallery (coming soon)",
        "gallery-recent": "Recent thumbnails",
        "join-title": "Join",
        "join-intro": ("Join the Python Togo community by filling out the form below."),
        "label-name": "Name",
        "label-fullname": "Full name",
        "label-email": "Email",
        "label-city": "City",
        "label-level": "Python level",
        "level-beginner": "Beginner",
        "level-intermediate": "Intermediate",
        "level-advanced": "Advanced",
        "btn-send": "Send",
        "contact-title": "Contact",
        "contact-intro": ("For any questions, send us a message using the form."),
        "label-subject": "Subject",
        "label-message": "Message",
        "agree-privacy": "I have read and agree to the privacy policy",
        "agree-coc": "I have read and agree to the Code of Conduct",
        "consent-alert": (
            "Please accept the privacy policy and Code of Conduct before continuing."
        ),
        "privacy-link-text": "Privacy Policy",
        "news-title": "News",
        "news-read-more": "Read more",
        "news-back": "Back to news",
        "privacy-title": "Privacy Policy",
        "privacy-heading": "Privacy Policy",
        "privacy-intro": (
            "At Python Togo, we take your data privacy seriously. This page "
            "explains what data we collect, why we collect it, and how we use "
            "it."
        ),
        "privacy-collect-heading": "Data we collect",
        "privacy-collect-1": (
            "Contact data: name, email address, phone (if provided) when you "
            "fill out a form."
        ),
        "privacy-collect-2": (
            "Profile information: city, level, interests (when you share them)."
        ),
        "privacy-collect-3": (
            "Technical data: IP address, browser type, and request timing to "
            "improve our services."
        ),
        "privacy-why-heading": "Why we collect this data",
        "privacy-why-intro": "We use your data to:",
        "privacy-why-1": "Respond to your requests (membership, partnership, contact).",
        "privacy-why-2": "Organize and inform about events.",
        "privacy-why-3": "Improve the site experience and security.",
        "privacy-share-heading": "Sharing and retention",
        "privacy-share-text": (
            "We do not sell or rent your personal data. Requests we receive "
            "may be shared with organizing members and kept as long as "
            "necessary to respond or comply with legal obligations."
        ),
        "privacy-retention-sub": "Retention period",
        "privacy-retention-intro": (
            "We retain your data as long as necessary to achieve the purposes "
            "for which it was collected. For example:"
        ),
        "privacy-retention-1": (
            "Membership requests: kept for 3 years after the last interaction, "
            "unless you request deletion."
        ),
        "privacy-retention-2": (
            "Event registrations: kept for the time needed to organize and "
            "archived for 3 years for administrative reasons."
        ),
        "privacy-retention-3": (
            "Contact messages: kept for 2–3 years depending on the nature of "
            "the request."
        ),
        "privacy-disclosure-sub": "Sharing and disclosure",
        "privacy-disclosure-text": (
            "We do not share your personal data with third parties for "
            "commercial purposes without your explicit consent. Data may be "
            "shared with providers processing data on our behalf (hosting, "
            "email delivery) under confidentiality agreements."
        ),
        "privacy-rights-heading": "Your rights",
        "privacy-rights-text": (
            "You can request access, rectification, or deletion of your data "
            "by emailing"
        ),
        "privacy-forms-heading": "Forms and consent",
        "privacy-forms-intro": (
            "All key forms (membership, partnership) require your explicit consent:"
        ),
        "privacy-forms-privacy": (
            "You must check the box indicating you have read and accepted our "
            "privacy policy."
        ),
        "privacy-forms-coc": (
            "You must check the box indicating you accept the community's Code "
            "of Conduct."
        ),
        "privacy-questions": ("If you have questions about this policy, contact us at"),
        "coc-title": "Code of Conduct",
        "coc-heading": "Code of Conduct",
        "coc-intro": (
            "This charter draws on best practices used by Python communities, "
            "including the Python Software Foundation (PSF). It aims to ensure "
            "a safe, welcoming, and professional environment for everyone, "
            "regardless of experience, identity, or background."
        ),
        "coc-commitment": "Our commitment",
        "coc-commitment-intro": "We commit to:",
        "coc-commitment-1": (
            "Provide an inclusive and respectful space for events, forums, and "
            "online channels related to Python Togo."
        ),
        "coc-commitment-2": "Value diverse backgrounds and contributions.",
        "coc-commitment-3": (
            "Respond quickly and confidentially to reports of inappropriate behavior."
        ),
        "coc-expected": "Expected behavior",
        "coc-expected-1": "Respect other participants and their opinions.",
        "coc-expected-2": ("Be mindful of language and use a constructive tone."),
        "coc-expected-3": (
            "Accept feedback humbly and be willing to apologize when wrong."
        ),
        "coc-expected-4": (
            "Respect venue- or platform-specific rules (moderation, safety, "
            "accessibility)."
        ),
        "coc-unacceptable": "Unacceptable behavior",
        "coc-unacceptable-intro": "The following will not be tolerated:",
        "coc-unacceptable-1": (
            "Discriminatory remarks, harassment, personal attacks, or threats."
        ),
        "coc-unacceptable-2": (
            "Insults; sexist, racist, homophobic, or transphobic remarks; or "
            "any hateful content."
        ),
        "coc-unacceptable-3": (
            "Sharing personal or confidential information without consent."
        ),
        "coc-unacceptable-4": (
            "Failing to follow safety and moderation guidelines from organizers."
        ),
        "coc-scope": "Scope",
        "coc-scope-text": (
            "This code applies to all official spaces and events organized by "
            "Python Togo, including in-person meetings, workshops, "
            "conferences, mailing lists, forums, and associated online "
            "channels."
        ),
        "coc-report": "Reporting procedure",
        "coc-report-intro": (
            "If you are a victim or witness of unacceptable behavior:"
        ),
        "coc-report-1": ("First, contact the organizers via the contact page or email"),
        "coc-report-2": (
            "Provide as many details as possible: date, location, people "
            "involved, witnesses, and message copies if relevant."
        ),
        "coc-report-3": (
            "Indicate if you wish your report to be handled confidentially."
        ),
        "coc-handling": "Handling reports",
        "coc-handling-text": (
            "Organizers will review reports promptly and take proportionate "
            "measures, which may include:"
        ),
        "coc-handling-1": "A formal warning.",
        "coc-handling-2": "Suspension or exclusion from an event or channel.",
        "coc-handling-3": ("Informing authorities if necessary."),
        "coc-confidentiality": "Confidentiality and protection",
        "coc-confidentiality-text": (
            "Information received in connection with a report will be handled "
            "with the greatest possible confidentiality. Only people "
            "necessary for the investigation will have access."
        ),
        "coc-examples": "Examples",
        "coc-examples-intro": "Examples of behaviors to report:",
        "coc-examples-1": (
            "Repeated, unsolicited messages from one individual targeting "
            "another person."
        ),
        "coc-examples-2": "Discriminatory comments based on identity.",
        "coc-examples-3": "Sharing a private photo without consent.",
        "coc-organizers": "Organizers' responsibilities",
        "coc-organizers-intro": "Organizers commit to:",
        "coc-organizers-1": ("Maintain clear procedures for incident handling."),
        "coc-organizers-2": (
            "Train moderators and leads, if needed, on handling reports."
        ),
        "coc-organizers-3": (
            "Publish updates on actions taken without compromising confidentiality."
        ),
        "coc-revision": "Revision",
        "coc-revision-text": (
            "This code of conduct may be reviewed periodically to reflect "
            "community feedback and international best practices."
        ),
        "coc-thanks": (
            "Thank you for helping make Python Togo a safe and welcoming space for all."
        ),
        "home-title": "Home",
        "home-welcome": "Welcome to Python Togo",
        "home-intro": (
            "Python Togo is a community of Python developers and enthusiasts in "
            "Togo. We organize events, trainings, and promote the use of "
            "Python across the country."
        ),
        "home-join": "Join the community",
        "home-view-events": "View events",
        "home-news-recent": "Recent news",
        "home-news-all": "See all news",
        "partners-our": "Our partners",
        "partners-intro": (
            "We thank the organizations and individuals who support us."
        ),
        "partners-none": "No partners yet.",
        "partners-request-title": "Request a partnership",
        "partners-request-intro": (
            "Would you like to support us or become a partner? Send your request below."
        ),
        "label-organization": "Organization",
        "label-contact-name": "Contact name",
        "label-website-optional": "Website (optional)",
        "label-message-optional": "Message (optional)",
        "partners-send": "Send request",
        "partners-sending": "Sending...",
        "partners-success": "Request sent, thank you!",
        "partners-error-prefix": "Error: ",
        "partners-network-error-prefix": "Network error: ",
        "about-title": "About",
        "about-heading": "About",
        "about-blurb": (
            "Python Togo brings together developers, students, and "
            "professionals using Python in Togo. Our mission is to promote "
            "learning and use of Python."
        ),
        "about-mission": "Our mission",
        "about-m1": "Promote learning and use of Python",
        "about-m2": "Organize events and training",
        "about-m3": "Encourage knowledge sharing",
        "events-title": "Events",
        "events-heading": "Events",
        "events-sample-meta": "2025-12-05 • Lomé",
        "events-sample-title": "Beginner Python workshop",
        "events-sample-desc": "Introduction to Python for new developers.",
        "communities-title": "Communities",
        "communities-heading": "Local communities",
        "communities-card-title": "Python Togo",
        "communities-card-desc": (
            "Local group based in Lomé, monthly meetups and workshops."
        ),
    },
}
DONATE_URL = "https://www.paypal.com/donate/?hosted_button_id=A6547S7YGMZ4A"


def get_language(request: Request) -> str:
    """
    Determine the preferred language for the request.

    Parameters
    ----------
    request : fastapi.Request
        The incoming HTTP request.

    Returns
    -------
    str
        The language code ("fr" or "en"). Defaults to "fr" if none matched.
    """
    cookie_lang = request.cookies.get("lang")
    if cookie_lang in TRANSLATIONS:
        return cookie_lang
    # Fallback to Accept-Language
    accept = request.headers.get("accept-language", "")
    if accept:
        for part in accept.split(","):
            code = part.split(";")[0].strip().lower()
            if code.startswith("fr"):
                return "fr"
            if code.startswith("en"):
                return "en"
    return "fr"


@app.get("/lang/{lang_code}")
async def set_language(lang_code: str, request: Request):
    """
    Set the UI language preference via cookie and redirect back.

    Parameters
    ----------
    lang_code : str
        Language code to set ("fr" or "en").
    request : fastapi.Request
        The incoming request, used to read referer.

    Returns
    -------
    fastapi.responses.RedirectResponse
        Redirects to the referer while setting the `lang` cookie.
    """
    if lang_code not in TRANSLATIONS:
        raise HTTPException(status_code=404, detail="Language not supported")
    referer = request.headers.get("referer") or "/"
    resp = RedirectResponse(url=referer, status_code=307)
    resp.set_cookie(
        "lang", lang_code, max_age=60 * 60 * 24 * 365, httponly=False, samesite="lax"
    )
    return resp


def ctx(request: Request, extra: Optional[dict] = None) -> dict:
    """
    Build the template context dictionary.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request used to derive language and cookies.
    extra : dict, optional
        Additional context values to merge.

    Returns
    -------
    dict
        The context including year, language, translations, and extras.
    """
    lang = get_language(request)
    base = {
        "current_year": current_year,
        "lang": lang,
        "t": TRANSLATIONS.get(lang, {}),
        "donate_url": DONATE_URL,
    }
    if extra:
        base.update(extra)
    return base


current_year = date.today().strftime("%Y")
# Configurable donate URL (set DONATE_URL env var). Defaults to '#'.


class JoinRequest(BaseModel):
    name: str
    email: str
    phone: str | None = None
    city: str | None = None
    level: str | None = None
    interests: str | None = None



class PartnershipRequest(BaseModel):
    organization: str
    contact_name: str
    email: str
    website: Optional[str] = None
    message: Optional[str] = None


class ContactSubmit(BaseModel):
    name: str
    email: str
    subject: str
    message: str
    agree_privacy: bool
    agree_coc: bool


def get_data(table):
    """Fetch all data from a given Supabase table.
    
    Parameters
    ----------
    table : str
        The name of the table to query.
    
    Returns
    -------
    list of dict
        The list of records from the table, or empty list on error.
    """
    try:
        response = supabase.table(table).select("*").execute()
        return response.data
    except Exception:
        return []

def insert_data(table, data):
    """Insert data into a given Supabase table.

    Parameters
    ----------
    table : str
        The name of the table to insert into.
    data : dict
        The data to insert.
    Returns
    -------
    bool
        True if insertion was successful, False otherwise.
    """
    try:
        supabase.table(table).insert(data).execute()
        return True
    except Exception as e:
        print(f"Error inserting data into {table}: {e}")
        return False

PARTNERS = get_data("partners")

GALLERIES = get_data("galleries")

JOIN_REQUESTS: List[dict] = []
CONTACT_MESSAGES: List[dict] = []


# Template routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the home page with recent news and partners.

    This view assembles recent news items and partner logos for display
    on the landing page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    See Also
    --------
    actualities : News listing page
    partners : Partners page

    Examples
    --------
    Access via browser: ``GET /``
    """
    lang = get_language(request)
    news_items = []
    for n in SAMPLE_NEWS:
        tr = n.get("translations", {}).get(lang, {})
        img = n.get("image") or f"https://picsum.photos/seed/news-{n['id']}/600/340"
        news_items.append(
            {
                "id": n["id"],
                "date": n["date"],
                "title": tr.get("title", ""),
                "excerpt": tr.get("excerpt", ""),
                "image": img,
            }
        )
    # show the most recent 2
    news_items = sorted(news_items, key=lambda x: x["date"], reverse=True)[:2]
    return templates.TemplateResponse(
        name="home.html",
        request=request,
        context=ctx(request, {"partners": PARTNERS, "news_home": news_items}),
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """
    Render the about page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /about``
    """
    return templates.TemplateResponse(
        name="about.html", request=request, context=ctx(request)
    )


@app.get("/events")
async def events(request: Request):
    """
    Render the events listing page using sample events data.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /events``
    """
    lang = get_language(request)
    items = []
    for e in SAMPLE_EVENTS:
        tr = e.get("translations", {}).get(lang, {})
        items.append(
            {
                "id": e["id"],
                "date": e["date"],
                "location": e.get("location", ""),
                "title": tr.get("title", ""),
                "description": tr.get("description", ""),
            }
        )
    items = sorted(items, key=lambda x: x["date"], reverse=True)
    return templates.TemplateResponse(
        request=request, name="events.html", context=ctx(request, {"events": items})
    )


@app.get("/events/{event_id}")
async def event_detail(event_id: int, request: Request):
    """
    Render a single event page.

    Parameters
    ----------
    event_id : int
        Identifier of the event to display.
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /events/1``
    """
    lang = get_language(request)
    found = next((e for e in SAMPLE_EVENTS if e["id"] == event_id), None)
    if not found:
        raise HTTPException(status_code=404, detail="Event not found")
    tr = found.get("translations", {}).get(lang, {})
    item = {
        "id": found["id"],
        "date": found["date"],
        "location": found.get("location", ""),
        "title": tr.get("title", ""),
        "description": tr.get("description", ""),
    }
    return templates.TemplateResponse(
        request=request, name="event_detail.html", context=ctx(request, {"item": item})
    )


@app.get("/actualities")
async def actualities(request: Request):
    """
    Render the news (actualities) listing page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /actualities``
    """
    lang = get_language(request)
    items = []
    for n in SAMPLE_NEWS:
        tr = n.get("translations", {}).get(lang, {})
        img = n.get("image") or f"https://picsum.photos/seed/news-{n['id']}/600/340"
        items.append(
            {
                "id": n["id"],
                "date": n["date"],
                "title": tr.get("title", ""),
                "excerpt": tr.get("excerpt", ""),
                "image": img,
            }
        )
    return templates.TemplateResponse(
        request=request, name="actualites.html", context=ctx(request, {"news": items})
    )


@app.get("/actualities/{news_id}")
async def news_detail(news_id: int, request: Request):
    """
    Render a single news page.

    Parameters
    ----------
    news_id : int
        Identifier of the news item.
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.

    Examples
    --------
    ``GET /actualities/2``
    """
    lang = get_language(request)
    found = next((n for n in SAMPLE_NEWS if n["id"] == news_id), None)
    if not found:
        raise HTTPException(status_code=404, detail="News not found")
    tr = found.get("translations", {}).get(lang, {})
    item = {
        "id": found["id"],
        "date": found["date"],
        "title": tr.get("title", ""),
        "body": tr.get("body", ""),
        "image": found.get("image")
        or f"https://picsum.photos/seed/news-{found['id']}/1200/680",
    }
    return templates.TemplateResponse(
        request=request, name="news_detail.html", context=ctx(request, {"item": item})
    )


@app.get("/communities")
async def communities(request: Request):
    """
    Render the communities page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    return templates.TemplateResponse(
        request=request, name="communities.html", context=ctx(request)
    )


@app.get("/join")
async def join(request: Request):
    """
    Render the join page (membership form).

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    return templates.TemplateResponse(
        request=request, name="join.html", context=ctx(request)
    )


@app.get("/contact")
async def contact(request: Request):
    """
    Render the contact page (contact form).

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    return templates.TemplateResponse(
        request=request, name="contact.html", context=ctx(request)
    )


@app.get("/code-of-conduct")
async def code_of_conduct(request: Request):
    """
    Render the Code of Conduct page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    return templates.TemplateResponse(
        request=request, name="code_of_conduct.html", context=ctx(request)
    )


@app.get("/partners")
async def partners(request: Request):
    """
    Render the partners page with current partners.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    return templates.TemplateResponse(
        request=request,
        name="partners.html",
        context=ctx(request, {"partners": PARTNERS}),
    )


@app.post("/api/v1/partnership")
async def partnership_submit(request: PartnershipRequest):
    """
    Receive partnership form submissions as JSON.

    Parameters
    ----------
    request : PartnershipRequest
        The validated partnership payload.

    Returns
    -------
    fastapi.responses.JSONResponse
        Status indicating receipt of the request.

    Examples
    --------
    ``POST /api/v1/partnership`` with JSON body
    """
    data = {}
    ct = request.headers.get("content-type", "")
    if "application/json" in ct:
        data = await request.json()
        data = PartnershipRequest(**data)
    else:
        form = await request.form()
        data = dict(form)
        data = PartnershipRequest(**data)
    
    try:
        validate_email(data.email, check_deliverability=True)
    except EmailNotValidError:
        return JSONResponse(
            status_code=400,
            content={"error": "Please use a valide email"},
        )

    # Normalize boolean fields
    agree_privacy = data.agree_privacy in (True, "true", "True", "on", "1", 1)
    agree_coc = data.agree_coc in (True, "true", "True", "on", "1", 1)
    if not agree_privacy or not agree_coc:
        return JSONResponse(status_code=400, content={"error": "consent_required"})
    
    data = json.dumps(data.dict())
    inserted = insert_data("partnershiprequest", data)
    if inserted:
        return JSONResponse(content={"status": "received"})
    else:
        return JSONResponse(content={"status": "Failed"})


@app.post("/api/v1/join")
async def join_submit(request: Request):
    """
    Receive join form submissions (JSON or form-encoded).

    Requires consent checkboxes to be set; otherwise returns 400.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request containing form or JSON payload.

    Returns
    -------
    fastapi.responses.JSONResponse
        Status indicating receipt of the request, or 400 on consent missing.
    """
    # Accept form-encoded or JSON
    data = {}
    ct = request.headers.get("content-type", "")
    if "application/json" in ct:
        data = await request.json()
        data = JoinRequest(**data)
    else:
        form = await request.form()
        data = dict(form)
        data = JoinRequest(**data)
    
    try:
        validate_email(data.email, check_deliverability=True)
    except EmailNotValidError:
        return JSONResponse(
            status_code=400,
            content={"error": "Please use a valide email"},
        )

    # Normalize boolean fields
    agree_privacy = data.agree_privacy in (True, "true", "True", "on", "1", 1)
    agree_coc = data.agree_coc in (True, "true", "True", "on", "1", 1)
    if not agree_privacy or not agree_coc:
        return JSONResponse(status_code=400, content={"error": "consent_required"})
    
    data = json.dumps(data.dict())
    inserted = insert_data("members", data)
    if inserted:
        return JSONResponse(content={"status": "received"})
    else:
        return JSONResponse(content={"status": "Failed"})


@app.post("/api/v1/contact")
async def contact_submit(request: Request):
    """
    Receive contact form submissions (JSON or form-encoded).

    Requires consent checkboxes to be set; otherwise returns 400.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request containing form or JSON payload.

    Returns
    -------
    fastapi.responses.JSONResponse
        Status indicating receipt of the message, or 400 on consent missing.
    """
    data = {}
    ct = request.headers.get("content-type", "")
    
    if "application/json" in ct:
        data = await request.json()
        data = ContactSubmit(**data)  # validate
    else:
        form = await request.form()
        data = dict(form)
        data = ContactSubmit(**data)

    try:
        validate_email(data.email, check_deliverability=True)
    except EmailNotValidError:
        return JSONResponse(
            status_code=400,
            content={"error": "Please use a valide email"},
        )
    
    agree_privacy = data.agree_privacy in (True, "true", "True", "on", "1", 1)
    agree_coc = data.agree_coc in (True, "true", "True", "on", "1", 1)
    if not agree_privacy or not agree_coc:
        return JSONResponse(status_code=400, content={"error": "consent_required"})

    data = json.dumps(data.dict())
 
    inserted = insert_data("contacts", data)
    if inserted:
        return JSONResponse(content={"status": "received"})
    else:
        return JSONResponse(content={"status": "Failed"})
    


@app.get("/gallery")
async def gallery(request: Request):
    """
    Render the gallery page with external links.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    return templates.TemplateResponse(
        request=request,
        name="gallery.html",
        context=ctx(request, {"galleries": GALLERIES}),
    )


@app.get("/privacy")
async def privacy(request: Request):
    """
    Render the privacy policy page.

    Parameters
    ----------
    request : fastapi.Request
        The incoming request.

    Returns
    -------
    fastapi.responses.HTMLResponse
        Rendered template response.
    """
    return templates.TemplateResponse(
        request=request, name="privacy.html", context=ctx(request)
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)

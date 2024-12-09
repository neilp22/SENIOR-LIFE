from typing import List, Optional
from datetime import date, datetime, timedelta
import re

# Classe abstracta Usuari
class Usuari:
    def __init__(self, id: int, nom: str, cognoms: str, sexe: str, data_naixement: date, 
                 dni: str, telefon: int, correu_electronic: str, contrasenya: str, data_registre: date):
        self.id = id
        self.nom = nom
        self.cognoms = cognoms
        self.sexe = sexe
        self.data_naixement = data_naixement
        self.dni = dni
        self.telefon = telefon
        self.correu_electronic = correu_electronic
        self.contrasenya = contrasenya
        self.data_registre = data_registre
        self.foto_perfil = None  # Foto de perfil opcional

    def validar_document_identificacio(self):
        # Valida el DNI, NIE o passaport
        dni_regex = r'^\d{8}[A-Za-z]$'
        nie_regex = r'^[XYZ]\d{7}[A-Za-z]$'
        passaport_regex = r'^\w{5,9}$'

        if re.match(dni_regex, self.dni) or re.match(nie_regex, self.dni) or re.match(passaport_regex, self.dni):
            return True
        return False

    def modificar_telefon(self, nou_telefon: int):
        self.telefon = nou_telefon

    def modificar_correu(self, nou_correu: str):
        self.correu_electronic = nou_correu

    def modificar_contrasenya(self, nova_contrasenya: str):
        self.contrasenya = nova_contrasenya

    def modificar_dades_personals(self, **dades):
        for clau, valor in dades.items():
            setattr(self, clau, valor)

# Subclasses
class Pacient(Usuari):
    def __init__(self, id: int, nom: str, cognoms: str, sexe: str, data_naixement: date, dni: str,
                 telefon: int, correu_electronic: str, contrasenya: str, data_registre: date,
                 grup_sanguini: str, cadira_rodes: bool, atributs_wearable: List['Wearable'],
                 contactes_emergencia: List[int], medicacions: List['Medicacio'],
                 metge_assignat: Optional['Metge'], infermer_assignat: Optional['Infermer'],
                 direccio: str, historial_medic: str):
        super().__init__(id, nom, cognoms, sexe, data_naixement, dni, telefon, correu_electronic, contrasenya, data_registre)
        self.grup_sanguini = grup_sanguini
        self.cadira_rodes = cadira_rodes
        self.atributs_wearable = atributs_wearable
        self.contactes_emergencia = contactes_emergencia
        self.medicacions = medicacions
        self.metge_assignat = metge_assignat
        self.infermer_assignat = infermer_assignat
        self.direccio = direccio
        self.historial_medic = historial_medic
        self.parametres_favorits = []

    def afegir_contacte_emergencia(self, contacte: int):
        self.contactes_emergencia.append(contacte)

    def eliminar_contacte_emergencia(self, contacte: int):
        self.contactes_emergencia.remove(contacte)

    def assignar_parametres_favorits(self, parametres: List[str]):
        if len(parametres) <= 3:
            self.parametres_favorits = parametres

    def confirmar_visita(self, visita: 'Visita'):
        visita.confirmada = True

    def rebutjar_visita(self, visita: 'Visita'):
        visita.confirmada = False

    def afegir_esdeveniment_social(self, calendari: 'Calendari', descripcio: str):
        calendari.afegir_esdeveniment("social", descripcio)

    def connectar_wearable(self, wearable: 'Wearable'):
        wearable.connectar_dispositiu()

    def generar_alerta_parametre(self, wearable: 'Wearable', parametre: str, valor: float, durada: timedelta):
        llindar = wearable.llindar.get(parametre)
        if llindar:
            if valor < llindar['min'] * 0.65 or valor > llindar['max'] * 1.65:
                return ("ALERTA CRÍTICA", f"{parametre} ({valor}) fora dels límits extremadament."
                        f" Notificant serveis d'emergència amb ubicació del pacient: {wearable.ubicacio}.")
            elif valor < llindar['min'] * 0.75 or valor > llindar['max'] * 1.35:
                return ("AVÍS MODERAT", f"{parametre} ({valor}) fora dels límits."
                        f" Notificant contactes d'emergència, metge i infermer assignats.")
        return "Paràmetre dins del rang normal."

class Familiar(Usuari):
    def __init__(self, id: int, nom: str, cognoms: str, sexe: str, data_naixement: date, dni: str,
                 telefon: int, correu_electronic: str, contrasenya: str, data_registre: date,
                 id_pacient: int, contacte_pacient: int, direccio: str):
        super().__init__(id, nom, cognoms, sexe, data_naixement, dni, telefon, correu_electronic, contrasenya, data_registre)
        self.id_pacient = id_pacient
        self.contacte_pacient = contacte_pacient
        self.direccio = direccio

    def verificar_pacient(self, pacients: List[Pacient]):
        for pacient in pacients:
            if pacient.dni == self.id_pacient:
                return True
        return False

class ProfessionalSanitari(Usuari):
    def __init__(self, id: int, nom: str, cognoms: str, sexe: str, data_naixement: date, dni: str,
                 telefon: int, correu_electronic: str, contrasenya: str, data_registre: date,
                 num_identificador: str, hospital_clinica: str):
        super().__init__(id, nom, cognoms, sexe, data_naixement, dni, telefon, correu_electronic, contrasenya, data_registre)
        self.num_identificador = num_identificador
        self.hospital_clinica = hospital_clinica

class Metge(ProfessionalSanitari):
    def __init__(self, id: int, nom: str, cognoms: str, sexe: str, data_naixement: date, dni: str,
                 telefon: int, correu_electronic: str, contrasenya: str, data_registre: date,
                 num_identificador: str, hospital_clinica: str, especialitat: str,
                 pacient: Optional[Pacient], registre_visita: List['Visita']):
        super().__init__(id, nom, cognoms, sexe, data_naixement, dni, telefon, correu_electronic, contrasenya, data_registre, num_identificador, hospital_clinica)
        self.especialitat = especialitat
        self.pacient = pacient
        self.registre_visita = registre_visita

    def validar_atributs_wearable(self, wearable: 'Wearable'):
        paràmetres_predefinits = {
            "passos": {"min": 0, "max": 10000},
            "freqüència cardíaca": {"min": 60, "max": 120},
            "electrocardiograma": {"min": 50, "max": 150},
            "temperatura": {"min": 36.1, "max": 37.2},
            "son": {"min": 4, "max": 9},
            "nivell d'oxigen": {"min": 95, "max": 100},
            "activitat física": {"min": 0, "max": 100}
        }
        for parametre, rang in paràmetres_predefinits.items():
            wearable.llindar[parametre] = rang

    def afegir_esdeveniment_clinic(self, calendari: 'Calendari', descripcio: str):
        calendari.afegir_esdeveniment("clinic", descripcio)

    def preescriure_medicacions(self, pacient: Pacient, medicacions: List['Medicacio']):
        pacient.medicacions.extend(medicacions)

    def programar_videotrucada(self, pacient: Pacient, data: date):
        return f"Videotrucada programada per al {data} amb el pacient {pacient.nom}."

class Infermer(ProfessionalSanitari):
    def __init__(self, id: int, nom: str, cognoms: str, sexe: str, data_naixement: date, dni: str,
                 telefon: int, correu_electronic: str, contrasenya: str, data_registre: date,
                 num_identificador: str, hospital_clinica: str, assistencia_domicili: bool):
        super().__init__(id, nom, cognoms, sexe, data_naixement, dni, telefon, correu_electronic, contrasenya, data_registre, num_identificador, hospital_clinica)
        self.assistencia_domicili = assistencia_domicili

    def registrar_visita(self, pacient: Pacient, visita: 'Visita'):
        pacient.historial_medic += f"\nVisita registrada: {visita.descripcio}"

    def preescriure_medicacions(self, pacient: Pacient, medicacions: List['Medicacio']):
        pacient.medicacions.extend(medicacions)

class Medicacio:
    def __init__(self, nom: str, descripcio: str, dates_per_tomar: List[date]):
        self.nom = nom
        self.descripcio = descripcio
        self.dates_per_tomar = dates_per_tomar
        self.marcat_com_pres = False

class Wearable:
    def __init__(self, nom: str, descripcio: str, parametres: List[str], ubicacio: str):
        self.nom = nom
        self.descripcio = descripcio
        self.parametres = parametres
        self.llindar = {}
        self.ubicacio = ubicacio
        self.connectat = False

    def connectar_dispositiu(self):
        self.connectat = True

class Calendari:
    def __init__(self, nom: str):
        self.nom = nom
        self.historial_esdeveniments_clinics = []
        self.historial_esdeveniments_socials = []

    def afegir_esdeveniment(self, tipus: str, descripcio: str):
        if tipus == "clinic":
            self.historial_esdeveniments_clinics.append(descripcio)
        elif tipus == "social":
            self.historial_esdeveniments_socials.append(descripcio)

    def eliminar_esdeveniment(self, tipus: str, descripcio: str):
        if tipus == "clinic":
            self.historial_esdeveniments_clinics.remove(descripcio)
        elif tipus == "social":
            self.historial_esdeveniments_socials.remove(descripcio)

    def obtenir_esdeveniments_per_data(self, data: date):
        return {
            "clinic": [ev for ev in self.historial_esdeveniments_clinics if ev.date() == data],
            "social": [ev for ev in self.historial_esdeveniments_socials if ev.date() == data]
        }

class Visita:
    def __init__(self, data_visita: date, tipus_visita: str, presencial_virtual: bool, descripcio: str):
        self.data_visita = data_visita
        self.tipus_visita = tipus_visita
        self.presencial_virtual = presencial_virtual
        self.descripcio = descripcio
        self.confirmada = False

class Formulari:
    def __init__(self, tipus_usuari: str, dades: dict):
        self.tipus_usuari = tipus_usuari
        self.dades = dades

    def validar_formulari(self):
        camps_obligatoris = ["nom", "cognoms", "dni", "telefon", "correu_electronic"]
        return all(camp in self.dades and self.dades[camp] for camp in camps_obligatoris)

    def generar_usuari(self):
        if self.tipus_usuari == "pacient":
            return Pacient(**self.dades)
        elif self.tipus_usuari == "familiar":
            return Familiar(**self.dades)
        elif self.tipus_usuari in ["metge", "infermer"]:
            return ProfessionalSanitari(**self.dades)

class PaginaInici:
    def __init__(self, calendari: Calendari, usuaris: List[Usuari]):
        self.calendari = calendari
        self.usuaris = usuaris

    def mostrar_notificacions(self):
        notificacions = []
        for usuari in self.usuaris:
            if isinstance(usuari, Pacient):
                if not usuari.validar_document_identificacio() or not usuari.metge_assignat:
                    notificacions.append(f"El formulari del pacient {usuari.nom} no està complet.")
            elif isinstance(usuari, Familiar):
                if not usuari.verificar_pacient(self.usuaris):
                    notificacions.append(f"El familiar {usuari.nom} no té pacient assignat.")
            elif isinstance(usuari, ProfessionalSanitari):
                if not usuari.num_identificador:
                    notificacions.append(f"El professional {usuari.nom} necessita completar el registre.")
        return notificacions

    def visualitzar_calendari(self, usuari: Usuari):
        if isinstance(usuari, (Familiar, ProfessionalSanitari)):
            return self.calendari.historial_esdeveniments_clinics
        elif isinstance(usuari,Pacient):
            return {
                "clinics": self.calendari.historial_esdeveniments_clinics,
                "socials": self.calendari.historial_esdeveniments_socials
            }

    def mostrar_medicacions_dia(self, pacient: Pacient, data_actual: date):
        medicacions_dia = [med.nom for med in pacient.medicacions if data_actual in med.dates_per_tomar]
        return medicacions_dia

    def mostrar_parametres_favorits(self, pacient: Pacient):
        return pacient.parametres_favorits

class PartSocial:
    def __init__(self):
        self.xats = {}
        self.comunitats = {}

    def iniciar_xat(self, usuari1: Usuari, usuari2: Usuari):
        clau = f"{usuari1.id}-{usuari2.id}"
        if clau not in self.xats:
            self.xats[clau] = []
        return f"Xat iniciat entre {usuari1.nom} i {usuari2.nom}."

    def enviar_missatge(self, usuari1: Usuari, usuari2: Usuari, missatge: str, imatge: Optional[str] = None):
        clau = f"{usuari1.id}-{usuari2.id}"
        if clau in self.xats:
            missatge_enviat = {"de": usuari1.nom, "missatge": missatge}
            if imatge:
                missatge_enviat["imatge"] = imatge
            self.xats[clau].append(missatge_enviat)
        return f"Missatge enviat de {usuari1.nom} a {usuari2.nom}."

    def iniciar_videotrucada(self, usuari1: Usuari, usuari2: Usuari):
        return f"Videotrucada iniciada entre {usuari1.nom} i {usuari2.nom}."

    def veure_ultims_missatges(self, usuari1: Usuari, usuari2: Usuari):
        clau = f"{usuari1.id}-{usuari2.id}"
        if clau in self.xats:
            return self.xats[clau][-10:]
        return []

    def unir_comunitat(self, usuari: Usuari, nom_comunitat: str):
        if nom_comunitat not in self.comunitats:
            self.comunitats[nom_comunitat] = []
        self.comunitats[nom_comunitat].append(usuari)
        return f"{usuari.nom} s'ha unit a la comunitat {nom_comunitat}."

    def veure_comunitat(self, nom_comunitat: str):
        if nom_comunitat in self.comunitats:
            comunitat = self.comunitats[nom_comunitat]
            membres = len(comunitat)
            return {"membres": membres, "usuaris": [usuari.nom for usuari in comunitat][:10]}
        return "Comunitat no trobada."

class PerfilUsuari:
    def __init__(self, usuari: Usuari):
        self.usuari = usuari

    def mostrar_dades_personals(self):
        dades = {
            "Nom": self.usuari.nom,
            "Cognoms": self.usuari.cognoms,
            "Data de naixement": self.usuari.data_naixement,
            "DNI": self.usuari.dni,
            "Telèfon": self.usuari.telefon,
            "Foto de perfil": self.usuari.foto_perfil
        }
        if isinstance(self.usuari, Pacient):
            dades.update({
                "Grup sanguini": self.usuari.grup_sanguini,
                "Cadira de rodes": self.usuari.cadira_rodes,
                "Direcció": self.usuari.direccio
            })
        elif isinstance(self.usuari, Familiar):
            dades.update({"ID pacient familiar": self.usuari.id_pacient})
        elif isinstance(self.usuari, Metge):
            dades.update({
                "Hospital de referència": self.usuari.hospital_clinica,
                "Número de col·legiat": self.usuari.num_identificador,
                "Especialitat": self.usuari.especialitat
            })
        elif isinstance(self.usuari, Infermer):
            dades.update({
                "Número de col·legiat": self.usuari.num_identificador,
                "Assistència domiciliària": self.usuari.assistencia_domicili
            })
        return dades

    def mostrar_parametres_wearable(self, wearable: Wearable):
        return wearable.parametres

# Dataset per a testeig
wearable1 = Wearable(
    nom="FitPro",
    descripcio="Dispositiu per monitorar la salut.",
    parametres=["freqüència cardíaca", "passos", "nivell d'oxigen"],
    ubicacio="Canell"
)
wearable1.llindar = {
    "freqüència cardíaca": {"min": 60, "max": 100},
    "passos": {"min": 0, "max": 10000},
    "nivell d'oxigen": {"min": 95, "max": 100}
}

pacient1 = Pacient(
    id=1,
    nom="Anna",
    cognoms="Martínez",
    sexe="F",
    data_naixement=date(1980, 6, 15),
    dni="12345678A",
    telefon=612345678,
    correu_electronic="anna.martinez@example.com",
    contrasenya="password123",
    data_registre=date(2023, 1, 1),
    grup_sanguini="O+",
    cadira_rodes=False,
    atributs_wearable=[wearable1],
    contactes_emergencia=[612345678],
    medicacions=[],
    metge_assignat=None,
    infermer_assignat=None,
    direccio="Carrer Major, 10",
    historial_medic="Historial inicial."
)

medicacio1 = Medicacio(
    nom="Paracetamol",
    descripcio="Per al dolor lleu.",
    dates_per_tomar=[date(2023, 3, 15)]
)
pacient1.medicacions.append(medicacio1)

calendari1 = Calendari(nom="Calendari de la Anna")
calendari1.afegir_esdeveniment("clinic", "Revisió anual amb el metge.")
calendari1.afegir_esdeveniment("social", "Aniversari de la filla.")

metge1 = Metge(
    id=2,
    nom="Dr. Joan",
    cognoms="Roca",
    sexe="M",
    data_naixement=date(1965, 11, 20),
    dni="23456789C",
    telefon=634567890,
    correu_electronic="dr.joan.roca@example.com",
    contrasenya="password789",
    data_registre=date(2023, 1, 3),
    num_identificador="1234MED",
    hospital_clinica="Hospital General",
    especialitat="Cardiologia",
    pacient=pacient1,
    registre_visita=[]
    )
pacient1.metge_assignat = metge1

infermer1 = Infermer(
    id=3,
    nom="Laura",
    cognoms="López",
    sexe="F",
    data_naixement=date(1990, 5, 18),
    dni="34567890D",
    telefon=645678901,
    correu_electronic="laura.lopez@example.com",
    contrasenya="password321",
    data_registre=date(2023, 1, 4),
    num_identificador="5678INF",
    hospital_clinica="Hospital General",
    assistencia_domicili=True
)
pacient1.infermer_assignat = infermer1

# Validació
print("Pacient 1:")
print(pacient1.nom, pacient1.dni, pacient1.grup_sanguini)
print("Metge assignat:", pacient1.metge_assignat.nom)
print("Infermer assignat:", pacient1.infermer_assignat.nom)
print("Wearable:", pacient1.atributs_wearable[0].nom)
print("Medicació del dia 15/03/2023:", pacient1.medicacions[0].nom)
print("Esdeveniments del calendari:", calendari1.historial_esdeveniments_clinics, calendari1.historial_esdeveniments_socials)

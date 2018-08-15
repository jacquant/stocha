# modules
import csv
import math
import random

from extension import SimulationOriginale
from load_config import load_config


class Simulation:
    """
    La classe simulation represente une simulation de file MMC selon les parametres charges dans
    le fichier config.ini.
    Attributs:
    ----------
    cadi_max: la valeur maximal que peut prendre un cadi lors de cette simulation
            :type: float
    benefice_cadi: le pourcentage de benefice qui sera pris par cadi lors de la simulation
            :type: float
    couts_rearrangement: le cout fixe que coute au magasin le depart d'un client
            :type: float
    cout_caisse: le cout d'une caisse pour une minute de fonctionnement
            :type: float
    variable_arrivee: la variable aleatoire de type exponentielle negative pour determiner le moment d'arriver
            :type: float
    variable_temps_service: la variable aleatoire de type exponentielle negative pour determiner le temps de traitement
            :type: float
    variable_attente_max: la variable aleatoire de type exponentielle negative pour determiner le temps d'attente
                          maximum
            :type: float
    beta: une variable aleatoire non-utilisee lors de notre simulation
            :type: float
    nbre_serveurs: le nombre de serveurs effectifs lors de la simulation
            :type: int
    temps_simulation: la duree de la simulation
            :type: float
    magasin: une instance de Magasin consideree pour la simulation
            :type: Magasin


    """

    def __init__(self, x, y, z, w, lam, mu, alpha, beta, nbre_serveurs, temps_simulation):
        """Constructeur de la classe Simulation. Instancie tous les attributs.

        :param x: la valeur maximal que peut prendre un cadi lors de cette simulation
        :type x: float
        :param y: le pourcentage de benefice qui sera pris par cadi lors de la simulation
        :type y: float
        :param z: le cout fixe que coute au magasin le depart d'un client
        :type z: float
        :param w: le cout d'une caisse pour une minute de fonctionnement
        :type w: float
        :param lam: la variable aleatoire de type exponentielle negative pour determiner le moment d'arriver
        :type lam: float
        :param mu: la variable aleatoire de type exponentielle negative pour determiner le temps de traitement
        :type mu: float
        :param alpha:la variable aleatoire de type exponentielle negative pour determiner le temps d'attente
                          maximum
        :type alpha: float
        :param beta: une variable aleatoire non-utilisee lors de notre simulation
        :type beta: float
        :param nbre_serveurs: le nombre de serveurs effectifs lors de la simulation
        :type nbre_serveurs: int
        :param temps_simulation: la duree de la simulation
        :type temps_simulation: float
        """
        self.cadi_max = x
        self.benefice_cadi = y
        self.couts_rearrangement = z
        self.cout_caisse = w
        self.variable_arrivee = lam
        self.variable_temps_service = mu
        self.variable_attente_max = alpha
        self.beta = beta
        self.nbre_serveurs = nbre_serveurs
        self.temps_simulation = temps_simulation
        self.magasin = self.Magasin(self.nbre_serveurs)
        self.recette = 0

    def simulation_magasin(self):
        """Simule le fonctionnement d'un magasin avec des clients impatients.
        """
        self.magasin.simule(self.variable_arrivee, self.variable_temps_service, self.temps_simulation,
                            self.benefice_cadi, self.cadi_max, self.couts_rearrangement, self.variable_attente_max)
        # Décommenter pour afficher les messages dans la console
        # print(self.magasin.donne_info_magasin())
        #print(self.donne_info_simulation())

        self.recette = self.magasin.benefice - self.magasin.couts_rearrangement - (
                self.nbre_serveurs * self.cout_caisse * self.temps_simulation)

    def donne_info_simulation(self):
        """Renvoie l'ensemble des informations statistiques produites lors de la simulation.

        :return texte: string contenant l'ensemble des informations statistiques de la simulation
        :rtype: str
        """
        esperance = self.magasin.donne_esperances()
        texte = "\nIl y a eu en moyenne " + str(
            esperance[0] / self.temps_simulation) + " clients dans le systeme pendant " \
                                                    "la simulation.\n"
        texte += "Il y a eu en moyenne " + str(esperance[1] / self.temps_simulation) + \
                 " clients dans une file pendant la simulation.\n"
        texte += "En moyenne, un client reste " + str(
            esperance[2] / self.magasin.nb_clients_total) + " minutes dans le magasin " \
                                                            "durant cette simulation.\n"
        texte += "En moyenne, un client reste " + str(
            esperance[3] / self.magasin.nb_clients_total) + " minutes dans une file " \
                                                            "durant cette simulation."
        texte += "\n-----------------------------------------------------------------------\n"
        texte += "La recette du magasin a ete de " + str(self.magasin.benefice) + " euros.\n"
        couts_fonctionnement = self.temps_simulation * self.cout_caisse + self.magasin.couts_rearrangement
        texte += "Les couts de fonctionnement du magasin ont ete de " + str(couts_fonctionnement) + " euros.\n"
        texte += "Le manque a gagner du magasin suite aux departs de clients est de " + \
                 str(self.magasin.manque_gagner + self.magasin.couts_rearrangement) + " euros.\n"
        texte += "\n-----------------------------------------------------------------------\n"
        texte += "Durant la simulation un total de %d clients sont rentres dans le systeme:\n \t %d ont ete traites " \
                 "tandis que \n \t%d n'ont pas ete traites" % (
                     self.magasin.nb_clients_total, self.magasin.nb_clients_traites, self.magasin.nb_clients_partis)
        return texte

    class Client:
        """La classe des clients represente la presence d'un client dans la simulation

        Attributs:
        ---------
        moment_arrivee: le moment ou le client arrive dans le magasin
                :type: float
        temps_service: le moment ou le client a ete servi
                :type: float
        cadi: le montant du cadi du client
                :type: float
        tolerance: le temps maximum que le client peut attendre dans la file
        """

        def __init__(self, arrivee, cadi_max, variable_attente_max):
            """Constructeur de la méthode
            :param arrivee: le moment ou le client est arrive dans le magasin
            :type arrivee: float
            :param cadi_max: le montant maximum que peut prendre un cadi
            :type cadi_max: float
            :param variable_attente_max: la variable aleatoire de type exponentielle negative
            :type variable_attente_max: float
            """
            self.moment_arrivee = arrivee
            self.temps_service = math.inf
            self.cadi = random.uniform(0, cadi_max)
            self.tolerance = random.expovariate(variable_attente_max)

        def donne_arrivee(self):
            """Donne le moment ou le client est arrive dans le magasin.

            :return: Le moment ou le client est arrive
            :rtype str
            """

            return str(self.moment_arrivee)

        def donne_temps_attente(self):
            """Donne le temps que le client a du attendre dans la file avant d'être à une caisse. En se basant sur la
            différence entre le moment où il a été servi et le moment où il est entré dans le magasin.

            :return: le temps que le client a attendu
            :rtype: float
            """
            return float(self.temps_service - self.moment_arrivee)

    class Caisse:
        """La classe caisse represente la presence d'une caisse au sein du magasin lors d'une simulation.

        Attributs:
        ---------
        num_caisse: le numero qui sert a identifier la caisse
                :type: int
        prochain_service:
                :type: float
        libre: L'etat de la caisse, occupee ou libre
                :type: bool
        clients_servis: La liste des clients qui ont ete servis durant la simulation par cette caisse
                :type: list
        """

        def __init__(self, identification):
            """Constructeur de la méthode

            :param identification: le numéro d'identification de la caisse
            :type identification: int
            """
            self.num_caisse = identification
            self.prochain_service = math.inf
            self.libre = True
            self.clients_servis = []

        def est_libre(self):
            return self.libre

        def change_occupation(self, valeur):
            self.libre = valeur

        def change_prochain_service(self, temps):
            self.prochain_service = temps

        def traiter_nouveau_client(self, client):
            self.clients_servis.append(client)

        def donne_info(self):
            info_caisse = "La caisse numero " + str(self.num_caisse) + " a servi ces clients:\n"
            for client in self.clients_servis:
                info_caisse += "\t%s\n" % client.donne_arrivee()
            info_caisse += "\nLa caisse numero %d a donc servi un total de %d clients" \
                           % (self.num_caisse, len(self.clients_servis))
            return info_caisse

    class Magasin:
        """La classe Magasin represente le fonctionnement d'un magasin pour la simulation.
        Attributs:
        ---------
        caisses: la liste contenant l'ensemble des caisses du magasin
                :type: list
        file: la liste des clients dans la file en attente d'etre traite
                :type: list
        clients: la liste des clients dans le magasin.
                :type: list
        nb_clients_total: le nombre de clients presents lors de la simulation
                :type: int
        nb_clients_traites: le nombre de clients qui ont ete traites.
                :type: int
        nb_clients_partis: le nombre de clients qui n'ont pas pu etre traites;
                :type: int
        benefice: le benefice que le magasin se fait de part son activite
                :type: float
        manque_gagner: le manque d'argent engendré par le depart de client
                :type: float
        couts_rearrangements: les couts que le magasin doit payer pour rearranger
                :type: float
        esperance_client_magasin: esperance du nombre de clients dans le magasin
                :type: float
        esperance_client_file: esperance du nombre de clients dans la file
                :type: float
        esperance_temps_magasin: esperance du temps de sejour dans le magasin
                :type: float
        esperance_temps_file: esperance du temps d'attente dans la file
                :type: float

        """

        def __init__(self, nbre_caisses):
            """Instancie les attributs de classe de Magasin en initialisant un certains nombre de Caisse.

            :param nbre_caisses: le nombre de caisses ouvertes durant la simulation
            :type nbre_caisses: int
            """
            self.caisses = []
            self.file = []
            self.clients = []
            self.nb_clients_total = 0
            self.nb_clients_traites = 0
            self.nb_clients_partis = 0
            self.benefice = 0
            self.manque_gagner = 0
            self.couts_rearrangement = 0
            self.esperance_client_magasin = 0
            self.esperance_client_file = 0
            self.esperance_temps_magasin = 0
            self.esperance_temps_file = 0
            for numero in range(nbre_caisses):
                self.caisses.append(Simulation.Caisse(numero))

        def simule(self, variable_arrivee, variable_temps_service, temps_simulation, benefice_cadi, cadi_max,
                   couts_rearrangement, variable_attente_max):
            """Simule le processus de files M/M/C au sein du magasin selon differente variable.

            :param variable_arrivee: la variable aleatoire de type exponentielle pour le temps d'arrivee
            :type variable_arrivee: float
            :param variable_temps_service: la variable aleatoire de type exponentielle pour le temps de service
            :type variable_temps_service: float
            :param temps_simulation: le temps en minutes de la simulation
            :type temps_simulation: float
            :param benefice_cadi: le pourcentage de benefice que se fait le magasin sur la valeur du cadi d'un client
            :type benefice_cadi: float
            :param cadi_max: le montant maximum que peut prendre un cadi
            :type cadi_max: float
            :param couts_rearrangement: le cout fixe que le magasin paye pour rearranger un cadi de client
            :type couts_rearrangement: float
            :param variable_attente_max: la variable aleatoire de type exponentielle negative
            :type variable_attente_max: float
            """
            # Initialisation
            nb_clients = 0
            temps = 0
            temps_prochaine_arrivee = random.expovariate(variable_arrivee)
            # Simulation
            while temps < temps_simulation:
                prochaine_caisse = self.donne_prochaine_caisse()
                temps_prochain_service = prochaine_caisse.prochain_service
                if temps_prochaine_arrivee <= temps_prochain_service:
                    temps_prochain_evenement = temps_prochaine_arrivee
                    client_arrive = True
                else:
                    temps_prochain_evenement = temps_prochain_service
                    client_arrive = False

                if temps_prochain_evenement < temps_simulation:
                    self.esperance_client_magasin += nb_clients * (temps_prochain_evenement - temps)
                    self.esperance_client_file += len(self.file) * (temps_prochain_evenement - temps)

                temps = temps_prochain_evenement  # On passe au moment du prochain evenement
                caisse_libre = self.donne_caisse_libre()

                if client_arrive and temps < temps_simulation:
                    client = Simulation.Client(temps, cadi_max, variable_attente_max)
                    nb_clients += 1
                    self.nb_clients_total += 1

                    # On genere la prochaine arrivee et on verifie qu'elle ne depasse pas le temps de la simulation
                    temps_prochaine_arrivee = temps + random.expovariate(variable_arrivee)

                    if temps_prochaine_arrivee < temps_simulation:
                        if caisse_libre:  # le client est traite par la caisse libre
                            caisse_libre.traiter_nouveau_client(client)
                            caisse_libre.change_occupation(False)
                            caisse_libre.change_prochain_service(temps +
                                                                 random.expovariate(variable_temps_service))
                            client.temps_service = caisse_libre.prochain_service
                            self.nb_clients_traites += 1
                            self.benefice += (client.cadi * benefice_cadi)
                            self.esperance_temps_magasin += (caisse_libre.prochain_service - temps)

                        else:  # le client doit attendre dans la file
                            self.file.append(client)
                    else:  # la prochaine arrivee est indeterminee
                        temps_prochaine_arrivee = math.inf

                elif not client_arrive:  # On va traiter un client
                    if len(self.file) != 0:  # Il y a des clients a traiter
                        client = self.file.pop()
                        client.temps_service = temps
                        if client.tolerance >= client.donne_temps_attente():  # le client est reste dans la file
                            # trop longtemps
                            prochaine_caisse.change_prochain_service(temps +
                                                                     random.expovariate(variable_temps_service))
                            prochaine_caisse.traiter_nouveau_client(client)
                            self.nb_clients_traites += 1
                            self.benefice += (client.cadi * benefice_cadi)
                            self.esperance_temps_file += client.donne_temps_attente()
                            self.esperance_client_magasin += (prochaine_caisse.prochain_service - temps)
                        else:  # le client a quitte la file
                            self.manque_gagner += (client.cadi * benefice_cadi)
                            self.couts_rearrangement += couts_rearrangement
                            self.nb_clients_partis += 1
                        nb_clients -= 1
                    else:  # Il n'y a aucun client a traiter
                        prochaine_caisse = self.donne_prochaine_caisse()
                        prochaine_caisse.change_occupation(True)
                        prochaine_caisse.change_prochain_service(math.inf)

        def donne_prochaine_caisse(self):
            """Renvoie la caisse qui peut traiter un client le plus rapidement parmi l'ensemble des caisses.

            :return: la caisse dont le temps avant le prochain service est le plus petit
            :rtype: Caisse
            """
            return min(self.caisses, key=lambda caisse: caisse.prochain_service)

        def donne_caisse_libre(self):
            """Renvoie la premiere caisse libre parmi la liste des caisses

            :return: renvoie la premiere caisse parmi la liste des caisses si pas renvoie None
            :rtype: Caisse
            """
            for caisse in self.caisses:
                if caisse.est_libre():
                    return caisse
            return None

        def donne_esperances(self):
            """Construit une liste des différentes esperances calculees pendant la simulation

            :return: La liste des différentes esperances (float) calculees pendant simule()
            :rtype : list
            """
            return [self.esperance_client_magasin, self.esperance_client_file,
                    self.esperance_temps_magasin, self.esperance_temps_file]

        def donne_info_magasin(self):
            """ Construit une variable string contenant toutes les informations du magasin et la renvoie.

            :return texte: Les informations des differentes caisses du magasin
            :rtype texte: str
            """

            texte = "Informations des differentes caisses du magasin.\n" + "________________________________________\n"
            for caisse in self.caisses:
                texte += caisse.donne_info()
                texte += "\n----------------------------------------\n"
            return texte


def simulation_masse():
    """
    Fait des simulations un grand nombre de fois et crée un fichier csv avec les résultats.
    """
    CONFIG = load_config()
    with open('simulation_normale1.csv', 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for a in range(10, 36):
            recettes = []
            for i in range(100):
                simulation = Simulation(float(CONFIG['CONSTANTE']['X']), float(CONFIG['CONSTANTE']['Y']),
                                        float(CONFIG['CONSTANTE']['Z']),
                                        float(CONFIG['CONSTANTE']['W']), float(CONFIG['VARIABLE']['lambda']),
                                        float(CONFIG['VARIABLE']['mu']),
                                        float(CONFIG['VARIABLE']['alpha']), float(CONFIG['VARIABLE']['beta']),
                                        a,
                                        float(CONFIG['SIMULATION']['temps_simulation']))

                simulation.simulation_magasin()
                recettes.append(simulation.recette)
            wr.writerow(recettes)


def simulation_originale_masse():
    """
    Fait des simulations un grand nombre de fois et crée un fichier csv avec les résultats.
    """
    CONFIG = load_config()
    with open('simulation_originale1.csv', 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for a in range(10, 36):
            recettes = []
            for i in range(100):
                simulation = SimulationOriginale(float(CONFIG['CONSTANTE']['X']), float(CONFIG['CONSTANTE']['Y']),
                                                 float(CONFIG['CONSTANTE']['Z']),
                                                 float(CONFIG['CONSTANTE']['W']), float(CONFIG['VARIABLE']['lambda']),
                                                 float(CONFIG['VARIABLE']['mu']),
                                                 float(CONFIG['VARIABLE']['alpha']), float(CONFIG['VARIABLE']['beta']),
                                                 a,
                                                 float(CONFIG['SIMULATION']['temps_simulation']))

                simulation.simulation_magasin()
                recettes.append(simulation.recette)
            wr.writerow(recettes)


def simulation_originale():
    CONFIG = load_config()
    simulation = SimulationOriginale(float(CONFIG['CONSTANTE']['X']), float(CONFIG['CONSTANTE']['Y']),
                                     float(CONFIG['CONSTANTE']['Z']),
                                     float(CONFIG['CONSTANTE']['W']), float(CONFIG['VARIABLE']['lambda']),
                                     float(CONFIG['VARIABLE']['mu']),
                                     float(CONFIG['VARIABLE']['alpha']), float(CONFIG['VARIABLE']['beta']),
                                     int(CONFIG['SIMULATION']['nombre_serveurs']),
                                     float(CONFIG['SIMULATION']['temps_simulation']))

    simulation.simulation_magasin()


if __name__ == "__main__":
    CONFIG = load_config()
    simulation = Simulation(float(CONFIG['CONSTANTE']['X']), float(CONFIG['CONSTANTE']['Y']),
                            float(CONFIG['CONSTANTE']['Z']),
                            float(CONFIG['CONSTANTE']['W']), float(CONFIG['VARIABLE']['lambda']),
                            float(CONFIG['VARIABLE']['mu']),
                            float(CONFIG['VARIABLE']['alpha']), float(CONFIG['VARIABLE']['beta']),
                            int(CONFIG['SIMULATION']['nombre_serveurs']),
                            float(CONFIG['SIMULATION']['temps_simulation']))
    #Commenter les différentes lignes en fonction de la simulation attendue
    # simulation.simulation_magasin()
    # simulation_originale()
    simulation_masse()
    simulation_originale_masse()

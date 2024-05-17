# JudgeGPT - (Fake) News Evaluation

JudgeGPT ist ein Forschungsprojekt, das sich auf die kritische Bewertung von Nachrichteninhalten konzentriert, die von KI erzeugt werden. Insbesondere wird untersucht, wie authentisch maschinell generierte im Vergleich zu menschlich generierten Nachrichten wahrgenommen werden. Diese frühe Arbeit zielt darauf ab, Erkenntnisse darüber zu gewinnen, wie Einzelpersonen zwischen echten und künstlichen Nachrichteninhalten unterscheiden.

Wenn Sie daran interessiert sind, diese Anwendung in Aktion zu sehen und an der Bewertung von Fake News teilzunehmen, besuchen Sie bitte unsere interaktive Umfrage unter [https://judgegpt.streamlit.app/](https://judgegpt.streamlit.app/).

## Projektübersicht

Der Kern von JudgeGPT liegt in seiner interaktiven Umfrageplattform, die mit Streamlit aufgebaut ist und Teilnehmer dazu einlädt, Nachrichtenfragmente zu lesen und zu beurteilen, ob sie glauben, dass die Inhalte von Menschen oder Maschinen erzeugt wurden. Dieser Prozess ist wichtig, um das öffentliche Verständnis zu ermitteln, aber auch um die Methoden zur Erkennung und Generierung von KI in zukünftigen Entwicklungen zu verfeinern. Das Projekt ist Teil einer größeren Forschungsinitiative und ergänzt unser Schwesterprojekt [RogueGPT](https://github.com/aloth/RogueGPT), das sich auf die Generierung von (Fake) Nachrichteninhalten konzentriert.

## Über den Namen: JudgeGPT

Der Name JudgeGPT wurde sorgfältig gewählt, um das Hauptziel dieses Forschungsprojekts zu reflektieren. Der Begriff "GPT" wird in einer pars pro toto Weise verwendet, wobei er nicht nur die von OpenAI entwickelten Generative Pre-trained Transformer Modelle bezeichnet, sondern ein breites Spektrum von großen Sprachmodellen (LLMs) abdeckt. Diese Wahl bedeutet, dass das Projekt zwar anfänglich auf Inhalte konzentriert ist, die von GPT-Modellen generiert wurden, aber im Wesentlichen darauf ausgelegt ist, Nachrichtenfragmente zu bewerten, die von jedem fortschrittlichen LLM erzeugt wurden. Das Wort "Judge" wird verwendet, da es sich direkt auf die Aktion bezieht, die die Teilnehmer im Rahmen des Projekts durchführen. Die Teilnehmer werden eingeladen, die ihnen präsentierten Nachrichtenfragmente zu beurteilen, um deren Authentizität (echt vs. gefälscht) und Herkunft (menschengeneriert vs. maschinengeneriert) zu bestimmen.

### Hauptkomponenten

- `app.py`: Das Hauptanwendungsskript, das die Streamlit-Webschnittstelle antreibt, den Umfrageprozess erleichtert, Daten sammelt und mit einer MongoDB-Datenbank für die Ergebnisverwaltung interagiert.

- `requirements.txt`: Eine einfache Datei, die alle notwendigen Python-Pakete auflistet, um eine einfache Einrichtung und Bereitstellung der JudgeGPT-Anwendung zu gewährleisten.

## Installation

Um an der Entwicklung von JudgeGPT teilzunehmen, folgen Sie diesen Schritten:

1. Klonen Sie das Repository auf Ihren lokalen Rechner.
2. Installieren Sie die erforderlichen Abhängigkeiten, die in `requirements.txt` aufgelistet sind, mit pip:

    ```bash
    pip install -r requirements.txt
    ```

3. Starten Sie die Streamlit-Anwendung:

    ```bash
    streamlit run app.py
    ```

## Nutzung

Beim Ausführen der Anwendung werden den Benutzern eine Reihe von Nachrichtenfragmenten angezeigt, die aus einer MongoDB-Datenbank abgerufen werden. Die Teilnehmer werden gebeten:

1. Jedes Nachrichtenfragment zu lesen.
2. Schieberegler zu verwenden, um ihre Wahrnehmung der Authentizität (echt vs. gefälscht) und der Quelle (Mensch vs. Maschine) des Fragments zu bewerten.
3. Ihre Antwort einzureichen und damit zum Forschungsdatensatz beizutragen.

Dieser iterative Prozess ermöglicht die Sammlung wertvoller Daten über die Wahrnehmung der Nachrichtenauthentizität, die in analytische Studien einfließen, die darauf abzielen, die Rahmenbedingungen für die Generierung und Erkennung von KI-Nachrichten zu verbessern.

### Sprachunterstützung und Spracherkennung

JudgeGPT zielt darauf ab, eine personalisierte Benutzererfahrung zu bieten, indem es automatisch Ihre Sprachpräferenz bestimmt, um den Umfrageinhalt entsprechend anzupassen. Sollten Sie jedoch Ihre bevorzugte Sprache manuell einstellen wollen, können Sie dies problemlos in der App ändern. Darüber hinaus ist es möglich, die Benutzersprache über URL-Parameter festzulegen. Um beispielsweise die Sprache auf Deutsch zu setzen, können Sie die URL [https://judgegpt.streamlit.app/?language=de](https://judgegpt.streamlit.app/?language=de) verwenden, oder für Französisch [https://judgegpt.streamlit.app/?language=fr](https://judgegpt.streamlit.app/?language=fr).

Derzeit unterstützt JudgeGPT die folgenden Sprachen:
- Englisch (`en`)
- Deutsch (`de`)
- Französisch (`fr`)
- Spanisch (`es`)

## Projektstatus

Als ein frühes Arbeitsprojekt entwickelt sich JudgeGPT kontinuierlich weiter, mit regelmäßigen Updates und Verbesserungen. Das Ziel ist es, den Umfang der Umfrage zu erweitern, die Benutzeroberfläche zu verbessern und die analytischen Aspekte des Projekts zu vertiefen, um reichhaltigere Einblicke in die Dynamik der Nachrichtenauthentizität im Zeitalter der KI zu bieten.

## Mitwirken

Beiträge zu JudgeGPT sind sehr willkommen, sei es in Form von Code-Verbesserungen, Datenbank-Erweiterungen oder analytischen Methodologien. Bei Interesse können Sie das Repository forken und Pull-Requests mit Ihren vorgeschlagenen Änderungen einreichen.

## Zukünftige Richtungen und Ideen zur Umsetzung

Während JudgeGPT ein grundlegendes Rahmenwerk für die Bewertung der Wahrnehmung von Nachrichtenauthentizität geschaffen hat, gibt es mehrere spannende Ideen, die noch umgesetzt werden sollen. Diese Verbesserungen zielen darauf ab, die Beteiligung zu vertiefen, die Benutzererfahrung zu bereichern und nuanciertere Einblicke in die gesammelten Daten zu bieten:

- **Lokalisierung**: Erweiterung der Plattform zur Unterstützung mehrerer Sprachen und regionaler Inhalte, um eine global inklusivere Forschungsperspektive zu ermöglichen. Dies würde die Sammlung von Daten über diverse sprachliche und kulturelle Kontexte hinweg ermöglichen und ein reichhaltigeres Verständnis der globalen Wahrnehmung von Nachrichtenauthentizität bieten.

- **Gamification**: Einführung von Spielelementen, um die Teilnahme zu fördern und den Bewertungsprozess spannender zu gestalten. Dazu könnten Punktesysteme, Abzeichen oder Bestenlisten gehören, um die Nutzer für ihre Beiträge und ihre Genauigkeit bei der Identifizierung von echten vs. gefälschten Nachrichten zu belohnen.

- **(Visualisierte) Ergebnisse**: Entwicklung eines interaktiven Dashboards, in dem die Teilnehmer die Echtzeitergebnisse und Erkenntnisse aus den gesammelten Daten einsehen können. Diese Visualisierung würde das Projekt nicht nur transparenter machen, sondern den Nutzern auch ermöglichen, Trends und Muster in der Nachrichtenwahrnehmung zu verstehen.

- **Personalisierte Feedback-Mechanismen**: Den Nutzern personalisiertes Feedback zu ihrer Leistung bieten, wie oft sie gefälschte Nachrichten korrekt identifizieren oder wie ihre Wahrnehmungen mit breiteren Trends übereinstimmen. Dies könnte die Nutzer weiter darin schulen, die Authentizität von Nachrichten zu erkennen.

## Lizenz

JudgeGPT ist Open-Source und unter der GNU GPLv3 Lizenz verfügbar. Für weitere Details siehe die LICENSE-Datei im Repository.

## Danksagungen

Dieses Projekt nutzt pymongo für die Datenbankinteraktionen.

## Haftungsausschluss

JudgeGPT ist ein unabhängiges Forschungsprojekt und steht in keiner Verbindung zu, wird nicht unterstützt von und ist in keiner Weise offiziell mit OpenAI verbunden. Die Verwendung von "GPT" im Projektnamen dient rein beschreibenden Zwecken und weist auf die Verwendung von generativen vortrainierten Transformermodellen als Kerntechnologie in unserer Forschung hin. Unsere Projekterkundungen und Ergebnisse sind unsere eigenen und spiegeln nicht die Ansichten oder Positionen von OpenAI oder deren Mitarbeitern wider. Wir verpflichten uns zu verantwortungsvoller KI-Forschung und halten uns an ethische Richtlinien in allen Aspekten unserer Arbeit, einschließlich der Generierung und Analyse von Inhalten.

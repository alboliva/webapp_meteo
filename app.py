import streamlit as st
import requests  # Per API meteo opzionale

# Configurazione app
st.set_page_config(page_title="App Meteo Roma", layout="wide")


# Home page
def home_page():
    st.title("Benvenuto in Meteo Rismi")

    # Riquadro sommario
    with st.expander("Sommario Condizioni Meteo, 8 Gennaio ore 1.38", expanded=True):
        # Testo personalizzato
        st.write("""
1. ANALISI SINOTTICA GENERALE \n
   Il quadro barico sull’Europa centro-meridionale è dominato da una circolazione depressionaria attiva sul Mediterraneo occidentale, con minimo principale tra Penisola Iberica e bacino algerino. Tale configurazione favorisce sull’Italia un flusso settentrionale e nord-orientale nei bassi strati, associato ad aria più fredda di origine continentale che scivola verso il Centro-Sud, mentre il Nord risente marginalmente di un campo di pressione più elevato. Le mappe di geopotenziale a 500 hPa mostrano una saccatura ben strutturata sul Mediterraneo, con asse inclinato NE–SW, responsabile di condizioni di instabilità diffusa sulle regioni centro-meridionali. Al suolo il gradiente barico risulta moderato, con ventilazione più sostenuta lungo le coste e sui mari esposti. La situazione si presenta sostanzialmente poco evolutiva nel breve termine, con tendenza alla persistenza dello schema sinottico almeno fino a 72 ore.

2. SITUAZIONE METEO PER AREE GEOGRAFICHE \n
   Al Nord prevalgono condizioni di stabilità atmosferica, con cieli in prevalenza sereni o poco nuvolosi. Nelle ore notturne e mattutine sono possibili foschie e banchi di nebbia nelle pianure interne e nei fondovalle, in dissolvimento nel corso della giornata. Le temperature minime risultano in diminuzione, con gelate locali, mentre le massime si mantengono stazionarie o in lieve aumento. Sui settori alpini di confine non si escludono locali addensamenti nuvolosi con deboli precipitazioni nevose a quote medio-alte.
   Al Centro il tempo si presenta più variabile. Sulle regioni tirreniche e sull’Appennino si osserva nuvolosità irregolare, talora compatta, con possibilità di deboli precipitazioni intermittenti, più probabili nelle ore pomeridiane e serali. Ventilazione debole o moderata dai quadranti settentrionali. Temperature minime in calo nelle aree interne, massime generalmente stazionarie.
   Al Sud e sulle Isole maggiori persistono condizioni di maggiore instabilità. Sono attesi annuvolamenti diffusi con precipitazioni sparse, localmente a carattere di rovescio, più frequenti lungo il basso Tirreno e sulle zone ioniche. Sui rilievi appenninici meridionali le precipitazioni potranno assumere carattere nevoso a quote medie. I venti risultano moderati o tesi, prevalentemente settentrionali, con mari mossi o molto mossi.

3. ANALISI DELLE MAPPE METEOROLOGICHE \n
   Le mappe di pressione al suolo evidenziano valori più bassi sul Mediterraneo occidentale e più elevati sull’Europa centro-orientale, configurando un flusso orientato da nord-est sull’Italia. Le mappe di temperatura mostrano anomalie negative più marcate al Centro-Sud, mentre il Nord si colloca su valori prossimi alla media stagionale. Le elaborazioni delle precipitazioni indicano accumuli generalmente modesti ma diffusi sulle regioni centro-meridionali, con distribuzione irregolare e fenomeni a carattere intermittente. Le mappe del vento confermano rinforzi lungo le coste tirreniche meridionali, adriatiche e ioniche, con raffiche localmente sostenute. L’analisi satellitare evidenzia nubi medio-basse estese sul Centro-Sud e ampie schiarite al Nord, mentre i radar mostrano celle precipitativi sparse e non organizzate.

4. EVOLUZIONE PREVISIONALE \n
   Nella giornata successiva è previsto il mantenimento dell’attuale configurazione, con ulteriore afflusso di aria fredda nei bassi strati verso il Centro-Sud. L’instabilità tenderà a concentrarsi sulle regioni meridionali e sulle Isole, mentre il Nord continuerà a beneficiare di condizioni più asciutte e stabili. Le temperature notturne rimarranno rigide, con diffuse gelate nelle zone interne. In una prospettiva a 72 ore, si intravede una graduale attenuazione dell’instabilità al Centro-Nord per il temporaneo rinforzo di un campo anticiclonico debole, mentre al Sud potranno persistere residui fenomeni legati alla circolazione ciclonica mediterranea.

5. CRITICITÀ METEOROLOGICHE \n
   Non si segnalano al momento criticità di elevata intensità. Restano tuttavia da monitorare le gelate notturne su pianure e valli interne del Nord e del Centro, le nevicate a quote medie sui rilievi meridionali e la ventilazione sostenuta con mare agitato sui bacini meridionali. Possibili disagi locali sono legati a precipitazioni improvvise e raffiche di vento nelle aree più esposte.

6. INDICI E CONSIDERAZIONI FINALI \n
   Il contesto termico risulta complessivamente in linea o lievemente inferiore alle medie stagionali, con maggiore anomalia negativa al Sud. L’indice di instabilità rimane moderato, sufficiente a generare rovesci sparsi ma non fenomeni organizzati di lunga durata. La situazione generale richiede un monitoraggio costante delle mappe sinottiche e dei dati osservativi, in quanto piccole variazioni nella posizione del minimo barico potrebbero determinare differenze significative nella distribuzione dei fenomeni, soprattutto sulle regioni centro-meridionali.
""")

# Esegui home (Streamlit gestisce multi-page automaticamente)
home_page()
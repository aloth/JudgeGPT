# JudgeGPT - Evaluación de Noticias (Falsas)

JudgeGPT es un proyecto de investigación enfocado en la evaluación crítica del contenido de noticias generadas por IA, explorando específicamente la percepción de autenticidad en noticias generadas por máquinas frente a las generadas por humanos. Este trabajo en etapa inicial tiene como objetivo recopilar información sobre cómo los individuos distinguen entre contenido de noticias real y artificial.

Si está interesado en ver esta aplicación en acción y le gustaría participar en la evaluación de noticias falsas, visite nuestra encuesta interactiva en [https://judgegpt.streamlit.app/](https://judgegpt.streamlit.app/).

## Resumen del Proyecto

El núcleo de JudgeGPT reside en su plataforma de encuesta interactiva, construida con Streamlit, que invita a los participantes a leer fragmentos de noticias y evaluar si creen que el contenido ha sido generado por humanos o máquinas. Este proceso es importante para entender la percepción pública pero también para refinar las metodologías de detección y generación de IA en futuros desarrollos. El proyecto es parte integral de una iniciativa de investigación más grande, complementando nuestro proyecto hermano [RogueGPT](https://github.com/aloth/RogueGPT), que se enfoca en la generación de contenido de noticias (falsas).

## Sobre el Nombre: JudgeGPT

El nombre JudgeGPT ha sido cuidadosamente elegido para reflejar el objetivo principal de este proyecto de investigación. El término "GPT" se emplea de manera pars pro toto, donde denota no solo los modelos Generative Pre-trained Transformer desarrollados por OpenAI sino que se extiende para cubrir un amplio espectro de Modelos de Lenguaje Grandes (LLMs). Esta elección significa que, aunque el proyecto pueda enfocarse inicialmente en contenido generado por modelos GPT, está inherentemente diseñado para evaluar fragmentos de noticias producidos por cualquier LLM avanzado. La palabra "Judge" se usa, ya que se relaciona directamente con la acción realizada por los participantes dentro del proyecto. Los asistentes están invitados a juzgar los fragmentos de noticias que se les presentan, determinando su autenticidad (real vs. falso) y origen (generado por humanos vs. generado por máquinas).

### Componentes Clave

- `app.py`: El script principal de la aplicación que alimenta la interfaz web de Streamlit, facilitando el proceso de encuesta, la recopilación de datos y la interacción con una base de datos MongoDB para el almacenamiento de resultados.

- `requirements.txt`: Un archivo simple que lista todos los paquetes de Python necesarios para asegurar una configuración e implementación fáciles de la aplicación JudgeGPT.

## Instalación

Para participar en el desarrollo de JudgeGPT, siga estos pasos:

1. Clone el repositorio en su máquina local.
2. Instale las dependencias requeridas listadas en `requirements.txt` usando pip:

    pip install -r requirements.txt

3. Inicie la aplicación Streamlit:

    streamlit run app.py

## Uso

Al ejecutar la aplicación, los usuarios son presentados con una serie de fragmentos de noticias recuperados de una base de datos MongoDB. Se pide a los participantes que:

1. Lean cada fragmento de noticias.
2. Utilicen deslizadores para calificar su percepción de la autenticidad del fragmento (real vs. falso) y la fuente (humano vs. máquina).
3. Envíen su respuesta, contribuyendo al conjunto de datos de investigación.

Este proceso iterativo permite la recopilación de datos valiosos sobre las percepciones de autenticidad de las noticias, alimentando estudios analíticos destinados a mejorar los marcos de generación y detección de noticias por IA.

### Soporte de Idiomas y Detección de Idiomas

JudgeGPT tiene como objetivo proporcionar una experiencia de usuario personalizada determinando automáticamente su preferencia de idioma para adaptar el contenido de la encuesta en consecuencia. Sin embargo, si desea establecer manualmente su idioma preferido, puede cambiarlo fácilmente en la aplicación. Además, es posible especificar el idioma del usuario a través de los parámetros de la URL. Por ejemplo, para establecer el idioma en alemán, puede usar la URL [https://judgegpt.streamlit.app/?language=de](https://judgegpt.streamlit.app/?language=de), o para el francés, [https://judgegpt.streamlit.app/?language=fr](https://judgegpt.streamlit.app/?language=fr).

Actualmente, JudgeGPT admite los siguientes idiomas:
- Inglés (`en`)
- Alemán (`de`)
- Francés (`fr`)
- Español (`es`)

## Estado del Proyecto

Como un trabajo en progreso temprano, JudgeGPT está en constante evolución, con actualizaciones y mejoras que se realizan regularmente. El objetivo es ampliar el alcance de la encuesta, mejorar la interfaz de usuario y profundizar en los aspectos analíticos del proyecto para proporcionar una comprensión más rica de la dinámica de la autenticidad de las noticias en la era de la IA.

## Contribuir

Las contribuciones a JudgeGPT son altamente alentadas, ya sea en forma de mejoras de código, mejoras de la base de datos o metodologías analíticas. Si está interesado, por favor bifurque el repositorio y envíe solicitudes de extracción con sus cambios propuestos.

## Direcciones Futuras e Ideas para Implementación

Aunque JudgeGPT ha establecido un marco fundamental para evaluar las percepciones de la autenticidad de las noticias, quedan varias ideas emocionantes por implementar. Estas mejoras tienen como objetivo profundizar el compromiso, enriquecer la experiencia del usuario y proporcionar perspectivas más matizadas sobre los datos recopilados:

- **Localización**: Ampliar la plataforma para admitir múltiples idiomas y contenido regional, permitiendo un alcance de investigación más inclusivo a nivel global. Esto permitiría la recopilación de datos a través de diversos contextos lingüísticos y culturales, ofreciendo una comprensión más rica de las percepciones globales de la autenticidad de las noticias.

- **Gamificación**: Introducción de elementos de gamificación para alentar la participación y hacer que el proceso de evaluación sea más atractivo. Esto podría incluir sistemas de puntuación, insignias o tablas de clasificación para recompensar a los usuarios por sus contribuciones y precisión en la identificación de noticias falsas vs. reales.

- **Resultados (Visualizados)**: Desarrollo de un tablero de control interactivo donde los participantes puedan ver los resultados en tiempo real y las perspectivas derivadas de los datos colectivos. Esta visualización no solo haría el proyecto más transparente, sino que también permitiría a los usuarios comprender las tendencias y patrones en la percepción de las noticias.

- **Mecanismos de Retroalimentación Personalizada**: Ofrecer a los usuarios retroalimentación personalizada sobre su rendimiento, como la frecuencia con la que identifican correctamente las noticias falsas o cómo se alinean sus percepciones con las tendencias más amplias. Esto podría también educar a los usuarios sobre cómo discernir la autenticidad de las noticias.

## Licencia

JudgeGPT es de código abierto y está disponible bajo la Licencia GNU GPLv3. Para más detalles, consulte el archivo LICENSE en el repositorio.

## Agradecimientos

Este proyecto utiliza pymongo para las interacciones con la base de datos.

## Descargo de Responsabilidad

JudgeGPT es un proyecto de investigación independiente y no está afiliado, respaldado ni de ninguna manera oficialmente conectado con OpenAI. El uso de "GPT" en el nombre de nuestro proyecto es puramente con fines descriptivos, indicando el uso de modelos de transformadores preentrenados generativos como tecnología central en nuestra investigación. Las exploraciones y hallazgos de nuestro proyecto son propios y no reflejan las opiniones o posiciones de OpenAI o sus colaboradores. Estamos comprometidos con la investigación responsable de IA y adherimos a directrices éticas en todos los aspectos de nuestro trabajo, incluida la generación y el análisis de contenido.

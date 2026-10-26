MediOrb UI package with animated robot video

Files in this package:
- app.py: Streamlit app with pink/cyan day mode and original dark-purple night mode
- styles.css: styling and animation rules
- mybot.mp4: animated robot video shown in the home-page hero

Keep these existing project files in the SAME folder as app.py:
- Memory_connect_with_llm.py
- report_analyzer.py
- any other modules/data required by your RAG project

Run from your activated virtual environment:
  python -m streamlit run app.py

The app starts in pink/cyan day mode. Toggle "Night mode" to switch to the original dark-purple theme.

The robot video is embedded as a muted, looping HTML video. Keep mybot.mp4 next to app.py.
This package does not include your RAG data, model/index files, or API secrets. Keep secrets out of source control.

from sqlmodel import Session, select, delete
from app.core.db import engine, create_db_and_tables
from app.models.db_models import Activity, ActivityQuestion

def seed():
    create_db_and_tables() 

    with Session(engine) as session:
        
        # Clear existing data for a fresh start
        session.exec(
            delete(ActivityQuestion).where(ActivityQuestion.activity_id == "mupac_guerras_cantabras")
        )
        
        session.exec(
            delete(Activity).where(Activity.activity_id == "mupac_guerras_cantabras")
        )

        session.commit() 
        
        act = Activity(activity_id="mupac_guerras_cantabras", name="MUPAC Guerras Cantabras 2025", description="Actividad sobre las guerras Cántabras para la MUPAC")
        session.add(act)

        q1 = ActivityQuestion(
            question_id="q01",
            activity_id="mupac_guerras_cantabras",
            contexto='''
            Bienvenido, joven historiador. En este viaje no vas solo a observar vitrinas, sino que vas a vivir la historia de las Guerras Cántabras desde dentro. Tu rol será doble: tendrás que investigar como arqueólogo y también ponerte en la piel de quienes lucharon en estas tierras entre los años 29 y 19 a.C., cuando César Augusto, primer emperador del Imperio Romano, la potencia más grande de la Antigüedad, decidió someter definitivamente a los cántabros. ¿Quiénes eran realmente los cántabros? ¿Cómo vivían? ¿Por qué opusieron tanta resistencia? Aquí descubrirás la respuesta a estas preguntas. 
            ''',
            pregunta="¿Empezamos?",
            respuesta_correcta="Respuesta esperada: afirmativa (sí, venga, vamos…)"
        )

        q2_1 = ActivityQuestion(
            question_id="q02.1",
            activity_id="mupac_guerras_cantabras",
            contexto="Tu primera misión es delimitar el territorio aproximado del pueblo de los antiguos cántabros, que no coincide exactamente con la actual Cantabria, e identificar los pueblos que hacían frontera con ellos.",
            pregunta="¿Con qué pueblos limitaban los cántabros tanto al este como al oeste?",
            respuesta_correcta="al este con los autrigones, y al oeste con los astures, aunque los cántabros se extendían por parte de la franja montañesa del oriente de la actual Asturias. Hay que entender que, en todo caso, no eran fronteras cerradas."
        )
        
        q2_2 = ActivityQuestion(
            question_id="q02.2",
            activity_id="mupac_guerras_cantabras",
            contexto="Tu primera misión es delimitar el territorio aproximado del pueblo de los antiguos cántabros, que no coincide exactamente con la actual Cantabria, e identificar los pueblos que hacían frontera con ellos.",
            pregunta="¿Y qué pasaba al sur? ¿Cuáles eran los límites y qué pueblos existían?",
            respuesta_correcta="Los cántabros llegaban al norte de Palencia y el norte de Burgos, zonas montañosas que precedían a la gran Meseta castellana. Hacían frontera con los turmogos (llanura burgalesa) y los vacceos (Tierra de Campos)."
        )

        q3 = ActivityQuestion(
            question_id="q03",
            activity_id="mupac_guerras_cantabras",
            contexto="Empecemos por un objeto misterioso: un gran caldero de bronce con dos asas circulares que fue hallado en Cabárceno y compone uno de los hallazgos más enigmáticos de tiempos del Bronce Final o de la Primera Edad del Hierro en Cantabria. Muchos arqueólogos piensan que se usaba en rituales sagrados o festines tribales. Se cree que guarda importante relación con los intercambios mantenidos con culturas de la costa atlántica europea, pues se han encontrado calderos similares en Irlanda o el sur de Inglaterra. Aunque no se trata de un objeto cántabro en sentido estricto, destaca por ser un antecedente cultural de esos pueblos que se enfrentaron al Imperio.",
            pregunta="¿Qué más crees que pudo representar? \nPoder del líder y conexión con lo divino\nTrofeo de guerra\nUtensilio doméstico",
            respuesta_correcta="A. Poder del líder y conexión con lo divino. Justificación: Tal vez se trató de un símbolo de prestigio que reforzaba la autoridad de los jefes de las tribus y su vínculo con lo divino."
        )

        q4_1 = ActivityQuestion(
            question_id="q04.1",
            activity_id="mupac_guerras_cantabras",
            contexto="Si hablásemos de símbolos cántabros… ¿cuál es el primero que se te vendría a la cabeza? El lábaro, por ejemplo, se trata de una recreación actual de alguno de los motivos que aparecen en las estelas discoideas gigantes, convirtiéndose en una de nuestras principales señas de identidad. Observa esas grandes estelas de más de un metro de diámetro, con marcas misteriosas.",
            pregunta="Por ejemplo, ¿qué ves en la estela de San Vicente de Toranzo?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger, pero preferentemente se espera que se responda un guerrero con lanza y caballo."
        )

        q4_2 = ActivityQuestion(
            question_id="q04.2",
            activity_id="mupac_guerras_cantabras",
            contexto="Si hablásemos de símbolos cántabros… ¿cuál es el primero que se te vendría a la cabeza? El lábaro, por ejemplo, se trata de una recreación actual de alguno de los motivos que aparecen en las estelas discoideas gigantes, convirtiéndose en una de nuestras principales señas de identidad. Observa esas grandes estelas de más de un metro de diámetro, con marcas misteriosas.",
            pregunta="Cerca, en la estela de Lombera, II hay un sol, una espiral y una serpiente. ¿Qué representa esta estela? \nEl Sol y la Luna\nUna deidad o personaje mítico con rayos en las manos \nUn símbolo del poder imperial",
            respuesta_correcta="A. El Sol y la Luna. Justificación: La estela parece expresar una visión cósmica donde Sol y Luna se complementan como fuerzas divinas, reflejando la dualidad vida/muerte o día/noche."
        )

        q4_3 = ActivityQuestion(
            question_id="q04.3",
            activity_id="mupac_guerras_cantabras",
            contexto="Si hablásemos de símbolos cántabros… ¿cuál es el primero que se te vendría a la cabeza? El lábaro, por ejemplo, se trata de una recreación actual de alguno de los motivos que aparecen en las estelas discoideas gigantes, convirtiéndose en una de nuestras principales señas de identidad. Observa esas grandes estelas de más de un metro de diámetro, con marcas misteriosas.",
            pregunta="¿Crees que estos símbolos ayudaban a los cántabros a enfrentarse al miedo a la muerte en la guerra?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger."
        )
        
        q5_1 = ActivityQuestion(
            question_id="q05.1",
            activity_id="mupac_guerras_cantabras",
            contexto="Ahora vas a entrar en el interior de una vivienda de la gens cantabrorum, nombre escogido por las fuentes latinas para referirse a estos pueblos. Descubre aquí dónde vivían.",
            pregunta="¿Cómo describirías la casa? ¿De qué materiales crees que estaría hecha?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger, pero preferentemente se espera que responda que las casas eran de planta circular u ovalada. Se realizaban con muros de entramado vegetal y barro, y zócalos de piedra."
        )

        q5_2 = ActivityQuestion(
            question_id="q05.2",
            activity_id="mupac_guerras_cantabras",
            contexto="Ahora vas a entrar en el interior de una vivienda de la gens cantabrorum, nombre escogido por las fuentes latinas para referirse a estos pueblos. Descubre aquí dónde vivían.",
            pregunta="Los antiguos cántabros tenían su hogar, su refugio, su bastión, y se organizaban en grandes castros fortificados. ¿Dónde crees que los construyeron?\nEn una llanura cerca del mar\nEn lo alto de una colina o monte\nEn el centro de un valle con ríos cerca",
            respuesta_correcta="B. En lo alto de una colina o monte. Justificación: Buscaban protegerse, controlar el territorio y tener ventaja en la defensa. Los cántabros no eran improvisados. Sus castros estaban bien situados, en lo alto, a veces a más de 800 metros de altitud, difíciles de alcanzar y rodeados de empalizadas de madera. Dominaban así visualmente su entorno y podían detectar ejércitos enemigos antes de que se acercaran. Además, estas cabañas, que se distribuían de forma adaptada a la pendiente, se agrupaban formando calles estrechas con este propósito."
        )

        q6 = ActivityQuestion(
            question_id="q06",
            activity_id="mupac_guerras_cantabras",
            contexto="Y… ¿cuál era la dieta de estos pueblos? Las fuentes clásicas de la conquista hablaban de una agricultura precaria, carne en tiempos de abundancia y de un predominio de la recolección de frutos silvestres (castañas, bellotas…). Sin embargo, esa visión ha sido discutida por la arqueología, y se sabe que los cántabros, como otros pueblos prerromanos, cultivaban al menos trigo, cebada y centeno y mantenían una cabaña compuesta por ganado vacuno, ovino, caprino y porcino.",
            pregunta="¿Por qué crees que los autores romanos tuvieron esa percepción de austeridad sobre la alimentación de los cántabros?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger, pero preferentemente se espera que se responda que los cántabros tenían una agricultura y una ganadería escasas, y que por eso se dedicaban a robar trigo a pueblos limítrofes, como los astures. A su vez, este es uno de los argumentos esgrimidos para explicar la conquista de los cántabros por parte de Roma: los saqueos a otros pueblos."
        )

        q7 = ActivityQuestion(
            question_id="q07",
            activity_id="mupac_guerras_cantabras",
            contexto="Encuentras una pequeña placa de bronce rota en dos piezas: la tésera de hospitalidad. Eran pactos sagrados, también conocidos como ‘hospitium’, entre pueblos o familias, que permitían el entendimiento mutuo, la protección y la cooperación comercial, lazos muy importantes en tiempos de guerra.",
            pregunta="¿Crees que el respeto por estos acuerdos facilitó la convivencia entre cántabros y romanos en algunos momentos?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger."
        )

        q8 = ActivityQuestion(
            question_id="q08",
            activity_id="mupac_guerras_cantabras",
            contexto="Te acercas a esa estatua, ¡que cobra vida! “¡Salve, joven cántabro! Permíteme presentarme: soy Cayo Julio César Octaviano Augusto, más conocido como Augusto, el primer emperador de Roma. A mis espaldas llevo la misión de pacificar un imperio tan vasto como jamás haya visto el mundo. Tras vencer en guerras civiles, fui proclamado princeps y asumí la tarea de someter los últimos rincones indómitos de Hispania.",
            pregunta="¿Quieres saber algún dato más sobre mí?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger."
        )

        q9_1 = ActivityQuestion(
            question_id="q09.1",
            activity_id="mupac_guerras_cantabras",
            contexto="Cansado de las rebeliones del norte y de que ni cántabros ni astures reconociesen mi autoridad desafiando la pax romana, decidí viajar personalmente para dirigir la campaña el año 26 a.C., y me instalé en Segisama (Burgos). Lanzamos ataques coordinados con columnas desde el sur, la costa y el interior, e incluso un desembarco en Portus Victoriae Iuliobrigensium de tropas desde Aquitania para cercas a los cántabros.",
            pregunta="¿Reconoces qué ciudad es hoy Portus Victoriae?",
            respuesta_correcta="Sí, Santander."
        )

        q9_2 = ActivityQuestion(
            question_id="q09.2",
            activity_id="mupac_guerras_cantabras",
            contexto="Cansado de las rebeliones del norte y de que ni cántabros ni astures reconociesen mi autoridad desafiando la pax romana, decidí viajar personalmente para dirigir la campaña el año 26 a.C., y me instalé en Segisama (Burgos). Lanzamos ataques coordinados con columnas desde el sur, la costa y el interior, e incluso un desembarco en Portus Victoriae Iuliobrigensium de tropas desde Aquitania para cercas a los cántabros.",
            pregunta="¿Conoces otras dos ciudades importantes que fundó Roma en la costa cántabra?",
            respuesta_correcta="Sí: Suances (Portus Blendium) y Castro Urdiales (Flaviobriga)."
        )

        q10 = ActivityQuestion(
            question_id="q10",
            activity_id="mupac_guerras_cantabras",
            contexto="Mis campañas están narradas en relatos que han llegado a nosotros fragmentados, incluida mi autobiografía perdida. Otros autores, como Tito Livio, Orosio o Floro, dejaron testimonios sobre el carácter belicoso de los cántabros. Floro, por ejemplo, afirmaba: “El primero en iniciar la rebelión, el más enérgico y pertinaz fue el de los cántabros, que, no contentos con defender su libertad, pretendían incluso imponer su dominio a sus vecinos y hostigaban con frecuentes incursiones a los vacceos, turmogos y autrigones”.",
            pregunta="Si tuvieses que definir en 5 pequeñas frases los motivos que tuvo el Imperio para conquistar a los cántabros, ¿cuáles dirías?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger, pero preferentemente se espera que se responda: los romanos querían controlar el hierro de las montañas cántabras, demostrar el prestigio y el poder de Augusto como emperador, terminar la conquista de Hispania, las razzias o saqueos de los cántabros a otros pueblos limítrofes e integrar la zona en la red económico-comercial romana."
        )

        q11 = ActivityQuestion(
            question_id="q11",
            activity_id="mupac_guerras_cantabras",
            contexto="Veamos ahora cómo fue la estrategia de ambos contendientes. En total, más de 70.000 soldados romanos participaron en alguna de las campañas militares, que se desarrollaban en verano. Frente a ellos, tribus dispersas, sin ejércitos regulares… pero con un conocimiento perfecto del terreno. Uno de los textos romanos conservados dice: “Los cántabros se mataban antes de ser capturados. Preferían morir a ser esclavos”.",
            pregunta="¿Cómo luchaban los cántabros frente a los romanos?\nEn formación cerrada, como las legiones\nCon armas largas y pesadas\nCon guerrillas, emboscadas y ataques rápidos desde las montañas",
            respuesta_correcta="C. Con guerrillas, emboscadas y ataques rápidos desde las montañas. Justificación: No podían enfrentarse directamente al ejército mejor entrenado del mundo. Los cántabros practicaban la guerra de guerrillas, pues conocían cada sendero, cada bosque, cada cueva. Se movían ligeros, golpeaban y desaparecían."
        )

        q12_1 = ActivityQuestion(
            question_id="q12.1",
            activity_id="mupac_guerras_cantabras",
            contexto="Ahora te diriges a una vitrina con algunas de las armas que se utilizaron en las batallas. \nLos cántabros usaban:\nEspadas cortas, ligeras, fáciles de manejar en bosques y montañas, y también puñales.\nLanzas: muy útiles para atacar desde lejos y también para defenderse.\nPuntas de flecha pequeñas de hierro: se usaban con arcos para atacar desde lugares altos o escondidos a distancia.\nEscudos circulares.\nPor su parte, los romanos:\nGladius: espada corta, recta y muy eficaz para luchar en grupo, junto al pugio (puñal).\nPilum: lanza que los romanos lanzaban antes de cargar.\nGrandes escudos rectangulares.\nMáquinas de guerra para arrojar proyectiles de diferentes tamaños (como el scorpio).",
            pregunta="Imagina que eres un joven cántabro durante la guerra. ¿Cómo te sentirías al ver llegar a los romanos? ¿Qué harías si tu familia quiere huir a las montañas?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger."
        )

        q12_2 = ActivityQuestion(
            question_id="q12.2",
            activity_id="mupac_guerras_cantabras",
            contexto="Ahora te diriges a una vitrina con algunas de las armas que se utilizaron en las batallas. \nLos cántabros usaban:\nEspadas cortas, ligeras, fáciles de manejar en bosques y montañas, y también puñales.\nLanzas: muy útiles para atacar desde lejos y también para defenderse.\nPuntas de flecha pequeñas de hierro: se usaban con arcos para atacar desde lugares altos o escondidos a distancia.\nEscudos circulares.\nPor su parte, los romanos:\nGladius: espada corta, recta y muy eficaz para luchar en grupo, junto al pugio (puñal).\nPilum: lanza que los romanos lanzaban antes de cargar.\nGrandes escudos rectangulares.\nMáquinas de guerra para arrojar proyectiles de diferentes tamaños (como el scorpio).",
            pregunta="¿Qué arma elegirías para defender tu castro y por qué?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger."
        )

        q13_1 = ActivityQuestion(
            question_id="q13.1",
            activity_id="mupac_guerras_cantabras",
            contexto="Tras casi diez años de lucha, los romanos impusieron su dominio en el 19 a.C., y empezaron a establecer su cultura y su civilización. Por ejemplo, en la vida cotidiana, puedes observar cómo se integraron objetos como lucernas para iluminar casas y termas o morillos, caballetes de hierro que se ponían en el hogar para sujetar la leña. Pero… ¿hasta qué punto Roma logró implantar sus costumbres en estos pueblos?",
            pregunta="¿Qué significa que Cantabria fue “romanizada”?\nQue los cántabros fueron exterminados\nQue adoptaron elementos de la cultura romana \nQue se convirtieron todos en soldados",
            respuesta_correcta="B. Que adoptaron elementos de la cultura romana. Justificación: La romanización fue una mezcla, un proceso parcial y que los cántabros no desaparecieron. Muchos se integraron (lengua, leyes, vías de comunicación, construcciones) en la administración romana, otros resistieron en la cultura popular, en los relatos orales. Entonces, hablaríamos de población cántabro-romana."
        )

        q13_2 = ActivityQuestion(
            question_id="q13.2",
            activity_id="mupac_guerras_cantabras",
            contexto="Tras casi diez años de lucha, los romanos impusieron su dominio en el 19 a.C., y empezaron a establecer su cultura y su civilización. Por ejemplo, en la vida cotidiana, puedes observar cómo se integraron objetos como lucernas para iluminar casas y termas o morillos, caballetes de hierro que se ponían en el hogar para sujetar la leña. Pero… ¿hasta qué punto Roma logró implantar sus costumbres en estos pueblos?",
            pregunta="Los romanos fundaron ciudades, pero… ¿cómo se llamó la más importante?",
            respuesta_correcta="Iuliobriga, cerca de Reinosa. Desde esta ciudad los romanos administraban el nuevo territorio, controlaban rutas, imponían el latín y el derecho romano"
        )

        q14 = ActivityQuestion(
            question_id="q14",
            activity_id="mupac_guerras_cantabras",
            contexto="En definitiva, la tradición se mantuvo, pues los romanos impusieron su cultura solo cuando era necesario para dominar y explotar el territorio. Tu viaje como joven cántabro finaliza visitando unas termas.",
            pregunta="¿Qué diferencias localizas en la vivienda, la alimentación y el ocio respecto a tu antigua cabaña en el castro?",
            respuesta_correcta="es una pregunta abierta, no hay opciones a escoger."
        )
        
        q15 = ActivityQuestion(
            question_id="q15",
            activity_id="mupac_guerras_cantabras",
            contexto="Misión completada. Has recorrido las Guerras Cántabras con ojos de arqueólogo y corazón de testigo. Ahora recuerda: la historia no es solo de los vencedores; la resistencia cántabra nos habla de libertad, de identidad, de paisaje y coraje. En el MUPAC has visto objetos reales que conectan dos mundos: el de la tribu y el del Imperio.",
            pregunta="No hay pregunta, este es el fin de la actividad.",
            respuesta_correcta="No hay respuesta, este es el fin de la actividad."
        )

        session.add_all([q1, q2_1, q2_2, q3, q4_1, q4_2, q4_3, q5_1, q5_2, q6, q7, q8, q9_1, q9_2, q10, q11, q12_1, q12_2, q13_1, q13_2, q14, q15])
        session.commit()

if __name__ == "__main__":
    seed()

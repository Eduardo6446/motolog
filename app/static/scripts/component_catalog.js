const COMPONENT_CATALOG = {

    aceite_motor: {
        nombre: "Aceite del Motor",
        descripcion: "Lubrica, enfría y protege los componentes internos del motor.",
        funcion_principal: "Reducir fricción, disipar calor y evitar desgaste prematuro.",
        sintomas_desgaste: [
            "Ruido excesivo del motor",
            "Sobrecalentamiento",
            "Consumo elevado de combustible"
        ],
        consecuencias: {
            normal: "El motor opera con menor eficiencia.",
            atencion: "Desgaste interno acelerado.",
            critico: "Daño severo o gripado del motor."
        },
        recomendacion_general: "Cambiar según el intervalo indicado y usar el aceite correcto.",
        impacto_seguridad: "Alto"
    },

    tamiz_aceite: {
        nombre: "Tamiz / Cedazo de Aceite",
        descripcion: "Filtra partículas gruesas antes de que el aceite circule por el motor.",
        funcion_principal: "Evitar que impurezas dañen componentes internos.",
        sintomas_desgaste: [
            "Aceite visiblemente sucio",
            "Mayor ruido del motor"
        ],
        consecuencias: {
            normal: "Filtrado menos eficiente.",
            atencion: "Circulación de partículas abrasivas.",
            critico: "Daño acelerado del motor."
        },
        recomendacion_general: "Limpiar en cada cambio de aceite cuando aplique.",
        impacto_seguridad: "Medio"
    },

    filtro_aceite: {
        nombre: "Filtro de Aceite",
        descripcion: "Retiene impurezas finas del aceite.",
        funcion_principal: "Proteger superficies internas del motor.",
        sintomas_desgaste: [
            "Aceite oscuro rápidamente",
            "Pérdida de presión"
        ],
        consecuencias: {
            normal: "Filtrado deficiente.",
            atencion: "Aceite contaminado circulando.",
            critico: "Daño interno grave."
        },
        recomendacion_general: "Reemplazar junto con el aceite.",
        impacto_seguridad: "Alto"
    },

    filtro_aire: {
        nombre: "Filtro de Aire",
        descripcion: "Impide la entrada de polvo y partículas al motor.",
        funcion_principal: "Garantizar combustión limpia.",
        sintomas_desgaste: [
            "Pérdida de potencia",
            "Mayor consumo",
            "Aceleración irregular"
        ],
        consecuencias: {
            normal: "Menor eficiencia.",
            atencion: "Desgaste interno progresivo.",
            critico: "Daño en cilindro y pistón."
        },
        recomendacion_general: "Limpiar o reemplazar según el entorno de uso.",
        impacto_seguridad: "Medio"
    },

    bujia: {
        nombre: "Bujía",
        descripcion: "Produce la chispa para la combustión.",
        funcion_principal: "Encender la mezcla aire–combustible.",
        sintomas_desgaste: [
            "Dificultad de arranque",
            "Fallas de encendido",
            "Vibraciones"
        ],
        consecuencias: {
            normal: "Arranque irregular.",
            atencion: "Pérdida de potencia.",
            critico: "El motor puede apagarse o no arrancar."
        },
        recomendacion_general: "Inspeccionar y reemplazar según intervalo.",
        impacto_seguridad: "Medio"
    },

    bujias: {
        nombre: "Bujías",
        descripcion: "Conjunto de bujías que permiten la combustión.",
        funcion_principal: "Encendido eficiente del motor.",
        sintomas_desgaste: [
            "Motor inestable",
            "Vibraciones"
        ],
        consecuencias: {
            normal: "Encendido irregular.",
            atencion: "Combustión deficiente.",
            critico: "Fallas constantes del motor."
        },
        recomendacion_general: "Reemplazar en conjunto.",
        impacto_seguridad: "Medio"
    },

    kit_arrastre: {
        nombre: "Cadena de Transmisión",
        descripcion: "Transmite la potencia del motor a la rueda trasera.",
        funcion_principal: "Permitir el desplazamiento de la motocicleta.",
        sintomas_desgaste: [
            "Ruidos metálicos",
            "Saltos de la cadena",
            "Vibraciones"
        ],
        consecuencias: {
            normal: "Desgaste progresivo.",
            atencion: "Pérdida de suavidad.",
            critico: "Rotura o pérdida de tracción."
        },
        recomendacion_general: "Lubricar y ajustar periódicamente.",
        impacto_seguridad: "Alto"
    },

    ajuste_valvulas: {
        nombre: "Holgura de Válvulas",
        descripcion: "Ajuste que garantiza apertura y cierre correcto de válvulas.",
        funcion_principal: "Optimizar admisión y escape.",
        sintomas_desgaste: [
            "Ruido metálico",
            "Pérdida de potencia"
        ],
        consecuencias: {
            normal: "Menor eficiencia.",
            atencion: "Desgaste de válvulas.",
            critico: "Daño severo del motor."
        },
        recomendacion_general: "Ajustar según kilometraje.",
        impacto_seguridad: "Medio"
    },

    liquido_frenos: {
        nombre: "Líquido de Frenos",
        descripcion: "Fluido hidráulico del sistema de frenos.",
        funcion_principal: "Transmitir presión de frenado.",
        sintomas_desgaste: [
            "Freno esponjoso",
            "Mayor distancia de frenado"
        ],
        consecuencias: {
            normal: "Respuesta menos precisa.",
            atencion: "Pérdida parcial de presión.",
            critico: "Falla total de frenos."
        },
        recomendacion_general: "Reemplazar cada 1–2 años.",
        impacto_seguridad: "Crítico"
    },

    zapatas_freno_delantero: {
        nombre: "Zapatas de Freno Delantero",
        descripcion: "Elementos de fricción del freno delantero.",
        funcion_principal: "Reducir velocidad y detener la moto.",
        sintomas_desgaste: [
            "Frenado débil",
            "Ruidos"
        ],
        consecuencias: {
            normal: "Mayor distancia de frenado.",
            atencion: "Desgaste del tambor.",
            critico: "Falla grave de frenado."
        },
        recomendacion_general: "Inspeccionar periódicamente.",
        impacto_seguridad: "Crítico"
    },

    zapatas_freno_trasero: {
        nombre: "Zapatas de Freno Trasero",
        descripcion: "Contribuyen al sistema de frenado trasero.",
        funcion_principal: "Estabilidad al frenar.",
        sintomas_desgaste: [
            "Freno poco efectivo"
        ],
        consecuencias: {
            normal: "Menor control.",
            atencion: "Desgaste del tambor.",
            critico: "Pérdida de frenado trasero."
        },
        recomendacion_general: "Inspección regular.",
        impacto_seguridad: "Alto"
    },

    pastillas_freno_delantero: {
        nombre: "Pastillas de Freno Delantero",
        descripcion: "Friccionan el disco para detener la motocicleta.",
        funcion_principal: "Frenado principal.",
        sintomas_desgaste: [
            "Chirridos",
            "Vibraciones"
        ],
        consecuencias: {
            normal: "Menor eficacia.",
            atencion: "Desgaste del disco.",
            critico: "Falla de frenado."
        },
        recomendacion_general: "Reemplazar antes del límite.",
        impacto_seguridad: "Crítico"
    },

    pastillas_freno_trasero: {
        nombre: "Pastillas de Freno Trasero",
        descripcion: "Friccionan el disco trasero.",
        funcion_principal: "Apoyo al frenado.",
        sintomas_desgaste: [
            "Respuesta lenta"
        ],
        consecuencias: {
            normal: "Menor control.",
            atencion: "Desgaste del disco.",
            critico: "Pérdida de estabilidad."
        },
        recomendacion_general: "Inspeccionar periódicamente.",
        impacto_seguridad: "Alto"
    },

    carburador: {
        nombre: "Carburador",
        descripcion: "Mezcla aire y combustible.",
        funcion_principal: "Alimentar correctamente el motor.",
        sintomas_desgaste: [
            "Consumo irregular",
            "Fallas de aceleración"
        ],
        consecuencias: {
            normal: "Menor eficiencia.",
            atencion: "Fallas de marcha.",
            critico: "El motor puede apagarse."
        },
        recomendacion_general: "Limpiar periódicamente.",
        impacto_seguridad: "Medio"
    },

    radiador_aceite: {
        nombre: "Radiador de Aceite",
        descripcion: "Disipa el calor del aceite.",
        funcion_principal: "Mantener temperatura óptima.",
        sintomas_desgaste: [
            "Sobrecalentamiento"
        ],
        consecuencias: {
            normal: "Temperatura elevada.",
            atencion: "Estrés térmico.",
            critico: "Daño grave del motor."
        },
        recomendacion_general: "Inspeccionar fugas y obstrucciones.",
        impacto_seguridad: "Alto"
    },

    frenos: {
        nombre: "Sistema de Frenos",
        descripcion: "Conjunto que permite detener la motocicleta.",
        funcion_principal: "Seguridad activa.",
        sintomas_desgaste: [
            "Mayor distancia de frenado",
            "Ruidos"
        ],
        consecuencias: {
            normal: "Menor capacidad.",
            atencion: "Respuesta impredecible.",
            critico: "Alto riesgo de accidente."
        },
        recomendacion_general: "Revisión completa periódica.",
        impacto_seguridad: "Crítico"
    }

};
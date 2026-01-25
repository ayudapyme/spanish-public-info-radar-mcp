"""BDNS prompts for grants and subsidies queries.

Prompts for the Base de Datos Nacional de Subvenciones (BDNS).
"""

from mcp.types import GetPromptResult, Prompt, PromptArgument, PromptMessage, TextContent

BDNS_PROMPTS: dict[str, Prompt] = {
    # =========================================================================
    # Search and Discovery
    # =========================================================================
    "convocatorias_abiertas": Prompt(
        name="convocatorias_abiertas",
        description="Find currently open grant calls. Shows active funding opportunities.",
        arguments=[
            PromptArgument(
                name="sector",
                description="Sector filter (e.g., 'tecnologia', 'agricultura', 'energia')",
                required=False,
            ),
        ],
    ),
    "subvenciones_ultimos_dias": Prompt(
        name="subvenciones_ultimos_dias",
        description="Recent grants published in the last N days.",
        arguments=[
            PromptArgument(
                name="dias",
                description="Number of days to look back (default: 7)",
                required=False,
            ),
        ],
    ),
    "subvenciones_por_organismo": Prompt(
        name="subvenciones_por_organismo",
        description="Find grants from a specific ministry or public body.",
        arguments=[
            PromptArgument(
                name="organismo",
                description="Name of the granting body (e.g., 'Ministerio de Industria')",
                required=True,
            ),
        ],
    ),
    "subvenciones_por_importe": Prompt(
        name="subvenciones_por_importe",
        description="Find grants by budget amount range.",
        arguments=[
            PromptArgument(
                name="importe_minimo",
                description="Minimum budget in euros",
                required=False,
            ),
            PromptArgument(
                name="importe_maximo",
                description="Maximum budget in euros",
                required=False,
            ),
        ],
    ),
    # =========================================================================
    # Beneficiary Analysis
    # =========================================================================
    "historial_beneficiario": Prompt(
        name="historial_beneficiario",
        description="Complete grant history for a specific beneficiary (company/entity).",
        arguments=[
            PromptArgument(
                name="nif",
                description="NIF/CIF of the beneficiary (e.g., B12345678)",
                required=True,
            ),
        ],
    ),
    "concesiones_recientes": Prompt(
        name="concesiones_recientes",
        description="Recently awarded grants in the last N days.",
        arguments=[
            PromptArgument(
                name="dias",
                description="Number of days to look back (default: 30)",
                required=False,
            ),
        ],
    ),
    "top_beneficiarios": Prompt(
        name="top_beneficiarios",
        description="Find entities that have received the most grants recently.",
        arguments=[
            PromptArgument(
                name="dias",
                description="Number of days to analyze (default: 90)",
                required=False,
            ),
        ],
    ),
    # =========================================================================
    # Detailed Analysis
    # =========================================================================
    "detalle_convocatoria": Prompt(
        name="detalle_convocatoria",
        description="Get complete details of a specific grant call.",
        arguments=[
            PromptArgument(
                name="id_convocatoria",
                description="BDNS grant call ID",
                required=True,
            ),
        ],
    ),
    "comparar_convocatorias": Prompt(
        name="comparar_convocatorias",
        description="Compare multiple grant calls side by side.",
        arguments=[
            PromptArgument(
                name="ids",
                description="Comma-separated list of BDNS IDs to compare",
                required=True,
            ),
        ],
    ),
    # =========================================================================
    # Sector-Specific
    # =========================================================================
    "subvenciones_innovacion": Prompt(
        name="subvenciones_innovacion",
        description="Find R&D and innovation grants.",
        arguments=[],
    ),
    "subvenciones_empleo": Prompt(
        name="subvenciones_empleo",
        description="Find employment and hiring incentive grants.",
        arguments=[],
    ),
    "subvenciones_pymes": Prompt(
        name="subvenciones_pymes",
        description="Find grants specifically for SMEs.",
        arguments=[],
    ),
    "subvenciones_autonomos": Prompt(
        name="subvenciones_autonomos",
        description="Find grants for self-employed workers.",
        arguments=[],
    ),
    "subvenciones_energia_verde": Prompt(
        name="subvenciones_energia_verde",
        description="Find grants for renewable energy and sustainability projects.",
        arguments=[],
    ),
    "subvenciones_digitalizacion": Prompt(
        name="subvenciones_digitalizacion",
        description="Find digital transformation grants (Kit Digital, etc.).",
        arguments=[],
    ),
}


def get_bdns_prompt_content(name: str, arguments: dict[str, str] | None = None) -> GetPromptResult:
    """Generate BDNS prompt content."""
    args = arguments or {}

    if name == "convocatorias_abiertas":
        sector = args.get("sector", "")
        sector_text = f" en el sector de {sector}" if sector else ""
        return GetPromptResult(
            description="Find open grant calls",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca convocatorias de subvenciones actualmente abiertas{sector_text}.

Pasos:
1. Usa search_grants para buscar convocatorias recientes (últimos 60 días)
2. Filtra las que tengan fecha de fin posterior a hoy
3. Para cada convocatoria abierta muestra:
   - Título
   - Organismo convocante
   - Presupuesto total
   - Fecha límite de solicitud
   - Enlace a las bases

Ordena por fecha límite (las más próximas primero).""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_ultimos_dias":
        dias = args.get("dias", "7")
        return GetPromptResult(
            description="Recent grants",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca las subvenciones publicadas en los últimos {dias} días.

Pasos:
1. Usa search_grants con date_from de hace {dias} días
2. Agrupa las convocatorias por:
   - Organismo convocante
   - Sector/temática
3. Muestra un resumen con:
   - Total de convocatorias publicadas
   - Presupuesto total disponible
   - Principales organismos convocantes
   - Lista de las más relevantes""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_por_organismo":
        organismo = args.get("organismo", "")
        return GetPromptResult(
            description=f"Grants from {organismo}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca todas las subvenciones convocadas por: {organismo}

Pasos:
1. Usa search_grants filtrando por granting_body
2. Lista las convocatorias encontradas:
   - Título y descripción
   - Presupuesto
   - Estado (abierta/cerrada)
   - Fechas de solicitud
3. Proporciona estadísticas:
   - Total de convocatorias
   - Presupuesto total gestionado
   - Sectores principales""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_por_importe":
        minimo = args.get("importe_minimo", "0")
        maximo = args.get("importe_maximo", "")
        rango = f"desde {minimo}€" + (f" hasta {maximo}€" if maximo else "")
        return GetPromptResult(
            description="Grants by amount",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Busca subvenciones con presupuesto {rango}.

Pasos:
1. Usa search_grants para obtener convocatorias recientes
2. Filtra por el rango de presupuesto indicado
3. Ordena de mayor a menor importe
4. Muestra:
   - Título
   - Presupuesto total
   - Organismo
   - Plazo de solicitud""",
                    ),
                ),
            ],
        )

    elif name == "historial_beneficiario":
        nif = args.get("nif", "")
        return GetPromptResult(
            description=f"Grant history for {nif}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Analiza el historial completo de subvenciones recibidas por la entidad con NIF: {nif}

Pasos:
1. Usa search_grant_awards con beneficiary_nif="{nif}"
2. Para cada concesión encontrada:
   - ID y fecha de concesión
   - Título de la convocatoria
   - Importe concedido
   - Organismo otorgante
3. Calcula estadísticas:
   - Total de subvenciones recibidas
   - Importe total acumulado
   - Principales organismos de los que recibe ayudas
   - Tendencia temporal (¿aumentan/disminuyen?)
4. Si hay convocatorias relevantes, usa get_grant_details para más información""",
                    ),
                ),
            ],
        )

    elif name == "concesiones_recientes":
        dias = args.get("dias", "30")
        return GetPromptResult(
            description="Recent grant awards",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Lista las subvenciones concedidas en los últimos {dias} días.

Pasos:
1. Usa search_grant_awards con date_from de hace {dias} días
2. Muestra:
   - Beneficiario
   - Importe concedido
   - Convocatoria de origen
   - Fecha de concesión
3. Proporciona estadísticas:
   - Total de concesiones
   - Importe total repartido
   - Principales beneficiarios""",
                    ),
                ),
            ],
        )

    elif name == "top_beneficiarios":
        dias = args.get("dias", "90")
        return GetPromptResult(
            description="Top grant recipients",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Identifica las entidades que más subvenciones han recibido en los últimos {dias} días.

Pasos:
1. Usa search_grant_awards para obtener concesiones recientes
2. Agrupa por beneficiario (NIF)
3. Calcula para cada uno:
   - Número de subvenciones
   - Importe total recibido
4. Ordena por importe total descendente
5. Muestra el top 20 de beneficiarios""",
                    ),
                ),
            ],
        )

    elif name == "detalle_convocatoria":
        id_conv = args.get("id_convocatoria", "")
        return GetPromptResult(
            description=f"Grant details {id_conv}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Obtén información detallada de la convocatoria BDNS: {id_conv}

Pasos:
1. Usa get_grant_details con grant_id="{id_conv}"
2. Muestra toda la información disponible:
   - Título completo y descripción
   - Organismo convocante
   - Presupuesto total
   - Fechas (publicación, inicio, fin)
   - Bases reguladoras (enlace)
   - Requisitos y condiciones
3. Si hay concesiones asociadas, usa search_grant_awards para ver beneficiarios""",
                    ),
                ),
            ],
        )

    elif name == "comparar_convocatorias":
        ids = args.get("ids", "")
        return GetPromptResult(
            description="Compare grants",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Compara las siguientes convocatorias: {ids}

Pasos:
1. Para cada ID, usa get_grant_details
2. Crea una tabla comparativa con:
   - Título
   - Organismo
   - Presupuesto
   - Fechas de solicitud
   - Beneficiarios objetivo
3. Destaca similitudes y diferencias
4. Recomienda cuál podría ser más adecuada según el perfil""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_innovacion":
        return GetPromptResult(
            description="R&D grants",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca subvenciones para I+D+i (investigación, desarrollo e innovación).

Pasos:
1. Usa search_grants buscando términos como "innovación", "I+D", "investigación", "tecnología"
2. Filtra las convocatorias activas
3. Agrupa por tipo:
   - Proyectos de investigación
   - Desarrollo tecnológico
   - Transferencia de conocimiento
   - Contratación de investigadores
4. Muestra las más relevantes con plazos y presupuestos""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_empleo":
        return GetPromptResult(
            description="Employment grants",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca subvenciones relacionadas con empleo y contratación.

Pasos:
1. Usa search_grants buscando "empleo", "contratación", "formación laboral"
2. Identifica programas como:
   - Bonificaciones a la contratación
   - Formación para el empleo
   - Inserción laboral de colectivos específicos
   - Emprendimiento
3. Muestra requisitos y cuantías de cada programa""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_pymes":
        return GetPromptResult(
            description="SME grants",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca subvenciones específicas para PYMES.

Pasos:
1. Usa search_grants buscando "PYME", "pequeña empresa", "mediana empresa"
2. Incluye programas de:
   - Digitalización
   - Internacionalización
   - Inversión productiva
   - Competitividad empresarial
3. Filtra por convocatorias abiertas
4. Muestra requisitos de elegibilidad y cuantías""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_autonomos":
        return GetPromptResult(
            description="Self-employed grants",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca ayudas y subvenciones para autónomos.

Pasos:
1. Usa search_grants buscando "autónomo", "trabajador por cuenta propia"
2. Incluye:
   - Cuota cero / tarifa plana
   - Ayudas al inicio de actividad
   - Capitalización del desempleo
   - Subvenciones sectoriales
3. Muestra requisitos y cuantías disponibles""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_energia_verde":
        return GetPromptResult(
            description="Green energy grants",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca subvenciones para energías renovables y sostenibilidad.

Pasos:
1. Usa search_grants buscando "renovable", "solar", "eficiencia energética", "sostenibilidad"
2. Incluye programas como:
   - Instalaciones fotovoltaicas
   - Autoconsumo energético
   - Rehabilitación energética de edificios
   - Movilidad eléctrica
   - Economía circular
3. Muestra cuantías y porcentajes de financiación""",
                    ),
                ),
            ],
        )

    elif name == "subvenciones_digitalizacion":
        return GetPromptResult(
            description="Digitalization grants",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text="""Busca subvenciones para transformación digital.

Pasos:
1. Usa search_grants buscando "digitalización", "Kit Digital", "digital"
2. Incluye programas de:
   - Kit Digital para PYMES
   - Comercio electrónico
   - Ciberseguridad
   - Cloud computing
   - Inteligencia artificial
3. Muestra convocatorias abiertas con plazos y requisitos""",
                    ),
                ),
            ],
        )

    else:
        raise ValueError(f"Unknown BDNS prompt: {name}")

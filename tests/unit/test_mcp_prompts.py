"""Tests for MCP prompts module."""

import pytest

from public_radar.prompts import (
    ALL_PROMPTS,
    BDNS_PROMPTS,
    BOE_PROMPTS,
    COMBINED_PROMPTS,
    DATOS_GOB_PROMPTS,
    INE_PROMPTS,
)
from public_radar.prompts.bdns import get_bdns_prompt_content
from public_radar.prompts.boe import get_boe_prompt_content
from public_radar.prompts.combined import get_combined_prompt_content
from public_radar.prompts.datos_gob import get_datos_gob_prompt_content
from public_radar.prompts.ine import get_ine_prompt_content


class TestPromptDefinitions:
    """Tests for prompt definitions."""

    def test_all_prompts_not_empty(self) -> None:
        """Test that ALL_PROMPTS dictionary is populated."""
        assert len(ALL_PROMPTS) > 0

    def test_all_prompts_have_name(self) -> None:
        """Test that all prompts have a name matching their key."""
        for key, prompt in ALL_PROMPTS.items():
            assert prompt.name == key

    def test_all_prompts_have_description(self) -> None:
        """Test that all prompts have a description."""
        for prompt in ALL_PROMPTS.values():
            assert prompt.description
            assert len(prompt.description) > 10

    def test_prompt_arguments_have_descriptions(self) -> None:
        """Test that all prompt arguments have descriptions."""
        for prompt in ALL_PROMPTS.values():
            if prompt.arguments:
                for arg in prompt.arguments:
                    assert arg.description
                    assert len(arg.description) > 5


class TestBdnsPrompts:
    """Tests for BDNS-related prompts."""

    def test_bdns_prompts_not_empty(self) -> None:
        """Test that BDNS prompts exist."""
        assert len(BDNS_PROMPTS) > 0

    def test_convocatorias_abiertas_content(self) -> None:
        """Test open grants prompt content."""
        result = get_bdns_prompt_content("convocatorias_abiertas")
        assert result.messages
        assert len(result.messages) == 1
        assert result.messages[0].role == "user"
        assert "search_grants" in result.messages[0].content.text

    def test_historial_beneficiario_content(self) -> None:
        """Test beneficiary history prompt content."""
        result = get_bdns_prompt_content("historial_beneficiario", {"nif": "B12345678"})
        assert "B12345678" in result.messages[0].content.text
        assert "search_grant_awards" in result.messages[0].content.text

    def test_subvenciones_innovacion_content(self) -> None:
        """Test innovation grants prompt content."""
        result = get_bdns_prompt_content("subvenciones_innovacion")
        assert "innovación" in result.messages[0].content.text or "I+D" in result.messages[0].content.text


class TestBoePrompts:
    """Tests for BOE-related prompts."""

    def test_boe_prompts_not_empty(self) -> None:
        """Test that BOE prompts exist."""
        assert len(BOE_PROMPTS) > 0

    def test_boe_hoy_content(self) -> None:
        """Test BOE summary prompt content."""
        result = get_boe_prompt_content("boe_hoy")
        assert "get_boe_summary" in result.messages[0].content.text

    def test_buscar_leyes_content(self) -> None:
        """Test legislation search prompt content."""
        result = get_boe_prompt_content("buscar_leyes", {"tema": "proteccion datos"})
        assert "proteccion datos" in result.messages[0].content.text
        assert "search_legislation" in result.messages[0].content.text

    def test_analizar_ley_content(self) -> None:
        """Test law analysis prompt content."""
        result = get_boe_prompt_content("analizar_ley", {"id": "BOE-A-2015-10566"})
        assert "BOE-A-2015-10566" in result.messages[0].content.text
        assert "get_legislation_details" in result.messages[0].content.text

    def test_borme_hoy_content(self) -> None:
        """Test BORME summary prompt content."""
        result = get_boe_prompt_content("borme_hoy")
        assert "get_borme_summary" in result.messages[0].content.text


class TestInePrompts:
    """Tests for INE-related prompts."""

    def test_ine_prompts_not_empty(self) -> None:
        """Test that INE prompts exist."""
        assert len(INE_PROMPTS) > 0

    def test_operaciones_estadisticas_content(self) -> None:
        """Test INE operations prompt content."""
        result = get_ine_prompt_content("operaciones_estadisticas")
        assert "get_ine_operations" in result.messages[0].content.text

    def test_ipc_inflacion_content(self) -> None:
        """Test IPC data prompt content."""
        result = get_ine_prompt_content("ipc_inflacion", {"periodos": "24"})
        assert "IPC" in result.messages[0].content.text
        assert "24" in result.messages[0].content.text

    def test_epa_paro_content(self) -> None:
        """Test unemployment prompt content."""
        result = get_ine_prompt_content("epa_paro")
        assert "EPA" in result.messages[0].content.text


class TestDatosGobPrompts:
    """Tests for datos.gob.es prompts."""

    def test_datos_gob_prompts_not_empty(self) -> None:
        """Test that datos.gob.es prompts exist."""
        assert len(DATOS_GOB_PROMPTS) > 0

    def test_explorar_catalogo_content(self) -> None:
        """Test catalog exploration prompt content."""
        result = get_datos_gob_prompt_content("explorar_catalogo")
        assert "list_open_data_themes" in result.messages[0].content.text

    def test_buscar_datasets_content(self) -> None:
        """Test dataset search prompt content."""
        result = get_datos_gob_prompt_content("buscar_datasets", {"busqueda": "calidad aire"})
        assert "calidad aire" in result.messages[0].content.text
        assert "search_open_data" in result.messages[0].content.text

    def test_analizar_dataset_content(self) -> None:
        """Test dataset analysis prompt content."""
        result = get_datos_gob_prompt_content("analizar_dataset", {"dataset_id": "test-123"})
        assert "test-123" in result.messages[0].content.text
        assert "get_open_data_details" in result.messages[0].content.text


class TestCombinedPrompts:
    """Tests for combined/research prompts."""

    def test_combined_prompts_not_empty(self) -> None:
        """Test that combined prompts exist."""
        assert len(COMBINED_PROMPTS) > 0

    def test_panorama_economico_content(self) -> None:
        """Test economic overview prompt content."""
        result = get_combined_prompt_content("panorama_economico")
        # Should reference multiple sources
        assert "INE" in result.messages[0].content.text
        assert "BOE" in result.messages[0].content.text
        assert "BDNS" in result.messages[0].content.text

    def test_investigar_empresa_content(self) -> None:
        """Test company investigation prompt content."""
        result = get_combined_prompt_content("investigar_empresa", {"nif": "B87654321", "nombre": "Acme Corp"})
        assert "B87654321" in result.messages[0].content.text
        assert "Acme Corp" in result.messages[0].content.text

    def test_analisis_sector_content(self) -> None:
        """Test sector analysis prompt content."""
        result = get_combined_prompt_content("analisis_sector", {"sector": "energia"})
        assert "energia" in result.messages[0].content.text
        # Should combine multiple sources
        assert "INE" in result.messages[0].content.text or "search_legislation" in result.messages[0].content.text


class TestPromptErrors:
    """Tests for prompt error handling."""

    def test_unknown_bdns_prompt_raises_error(self) -> None:
        """Test that unknown BDNS prompt raises ValueError."""
        with pytest.raises(ValueError, match="Unknown BDNS prompt"):
            get_bdns_prompt_content("prompt-que-no-existe")

    def test_unknown_boe_prompt_raises_error(self) -> None:
        """Test that unknown BOE prompt raises ValueError."""
        with pytest.raises(ValueError, match="Unknown BOE prompt"):
            get_boe_prompt_content("prompt-invalido")

    def test_unknown_ine_prompt_raises_error(self) -> None:
        """Test that unknown INE prompt raises ValueError."""
        with pytest.raises(ValueError, match="Unknown INE prompt"):
            get_ine_prompt_content("prompt-invalido")

    def test_unknown_datos_gob_prompt_raises_error(self) -> None:
        """Test that unknown datos.gob prompt raises ValueError."""
        with pytest.raises(ValueError, match="Unknown datos.gob.es prompt"):
            get_datos_gob_prompt_content("prompt-invalido")

    def test_unknown_combined_prompt_raises_error(self) -> None:
        """Test that unknown combined prompt raises ValueError."""
        with pytest.raises(ValueError, match="Unknown combined prompt"):
            get_combined_prompt_content("prompt-invalido")


class TestPromptCount:
    """Tests for expected prompt count."""

    def test_minimum_prompt_count(self) -> None:
        """Test that we have a minimum number of prompts."""
        assert len(ALL_PROMPTS) >= 50  # We have many prompts now

    def test_bdns_prompt_count(self) -> None:
        """Test BDNS prompts count."""
        assert len(BDNS_PROMPTS) >= 10

    def test_boe_prompt_count(self) -> None:
        """Test BOE prompts count."""
        assert len(BOE_PROMPTS) >= 20

    def test_ine_prompt_count(self) -> None:
        """Test INE prompts count."""
        assert len(INE_PROMPTS) >= 20

    def test_datos_gob_prompt_count(self) -> None:
        """Test datos.gob prompts count."""
        assert len(DATOS_GOB_PROMPTS) >= 15

    def test_combined_prompt_count(self) -> None:
        """Test combined prompts count."""
        assert len(COMBINED_PROMPTS) >= 15

    def test_all_sources_have_prompts(self) -> None:
        """Test that each data source has prompts."""
        assert len(BDNS_PROMPTS) > 0
        assert len(BOE_PROMPTS) > 0
        assert len(INE_PROMPTS) > 0
        assert len(DATOS_GOB_PROMPTS) > 0
        assert len(COMBINED_PROMPTS) > 0

    def test_no_duplicate_prompt_names(self) -> None:
        """Test that there are no duplicate prompt names across categories."""
        all_names = (
            list(BDNS_PROMPTS.keys())
            + list(BOE_PROMPTS.keys())
            + list(INE_PROMPTS.keys())
            + list(DATOS_GOB_PROMPTS.keys())
            + list(COMBINED_PROMPTS.keys())
        )
        assert len(all_names) == len(set(all_names)), "Duplicate prompt names found"

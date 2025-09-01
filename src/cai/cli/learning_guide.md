# Guia Completo: Implementação de Aprendizado Contínuo no CAI

## Visão Geral

Este guia demonstra como implementar e utilizar o sistema de aprendizado contínuo (Continuous Learning) no CAI, permitindo que o framework aprenda com interações passadas e melhore seu desempenho ao longo do tempo.

## Arquitetura do Sistema de Aprendizado

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Interações    │───▶│  Padrões de      │───▶│   Base de        │
│   do Usuário    │    │  Aprendizado     │    │   Conhecimento   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Análise de     │    │  Extração de     │    │   Aplicação de   │
│  Sessões        │    │  Padrões         │    │   Padrões        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Componentes Principais

### 1. ContinuousLearningEngine
- **Responsabilidade**: Motor principal de aprendizado
- **Funcionalidades**:
  - Extração de padrões de interações
  - Gerenciamento da base de conhecimento
  - Análise de sessões
  - Atualização de modelos

### 2. LearningIntegrationManager
- **Responsabilidade**: Integração com componentes existentes
- **Funcionalidades**:
  - Hooks de aprendizado
  - Gerenciamento de sessões
  - Aplicação de padrões aprendidos

### 3. EnhancedAgentRunner
- **Responsabilidade**: Execução de agentes com aprendizado
- **Funcionalidades**:
  - Rastreamento de interações
  - Aplicação de insights aprendidos
  - Feedback do usuário

## Configuração Inicial

### 1. Instalação e Setup

```python
from cai.cli.learning_config import setup_learning_environment
from cai.cli.learning_integration import initialize_learning_integration

# Configurar ambiente de aprendizado
success = setup_learning_environment()
if success:
    # Inicializar integração de aprendizado
    await initialize_learning_integration()
```

### 2. Configuração Personalizada

```python
from cai.cli.learning_config import get_learning_config

config = get_learning_config()

# Configurar modelo de aprendizado
config.update_model_config(
    model_name="openai/gpt-4o",
    temperature=0.3,
    max_tokens_per_analysis=2000
)

# Ajustar thresholds
config.set('learning_config.min_confidence_threshold', 0.8)
config.set('learning_config.learning_interval_minutes', 15)
```

## Uso Básico

### 1. Ativação do Aprendizado

```python
from cai.cli.enhanced_agent_runner import EnhancedAgentRunner
from cai.cli.learning_integration import get_learning_integration

# Criar runner com aprendizado
runner = EnhancedAgentRunner(console=console)
runner.enable_learning()

# Ou gerenciar globalmente
learning_manager = get_learning_integration()
learning_manager.enable_learning()
```

### 2. Execução com Aprendizado

```python
# Executar agente com aprendizado ativo
await runner.run_agent_conversation(
    agent=my_agent,
    user_input="Scan the network for vulnerabilities",
    context="network security assessment"
)

# O sistema automaticamente:
# 1. Aplica padrões aprendidos ao agente
# 2. Registra a interação para aprendizado futuro
# 3. Extrai novos padrões da resposta
```

### 3. Adição de Feedback

```python
# Adicionar feedback do usuário
runner.add_user_feedback(
    feedback="The scanning approach was very effective",
    rating=5
)

# Ou diretamente no manager
learning_manager.add_user_feedback(
    "Great at finding hidden services",
    rating=4
)
```

## Funcionalidades Avançadas

### 1. Análise de Sessões

```python
# Iniciar sessão de aprendizado
learning_manager.start_session("pentest_session_001")

# ... executar múltiplas interações ...

# Finalizar e analisar sessão
results = await learning_manager.end_session_and_learn()

print(f"Padrões descobertos: {results['patterns_discovered']}")
print(f"Total de padrões: {results['total_patterns']}")
```

### 2. Consulta de Insights

```python
# Obter insights relevantes para um contexto
insights = await learning_manager.get_learning_insights(
    "web application vulnerability scanning"
)

for insight in insights['insights']:
    print(f"Padrão: {insight['description']}")
    print(f"Confiança: {insight['confidence']:.2f}")
    print(f"Recomendações: {insight['recommendations']}")
```

### 3. Gerenciamento de Padrões

```python
from cai.cli.continuous_learning import get_learning_engine

engine = get_learning_engine()

# Obter estatísticas de aprendizado
stats = engine.get_learning_stats()
print(f"Padrões totais: {stats['total_patterns']}")
print(f"Confiança média: {stats['average_confidence']:.2f}")

# Buscar padrões específicos
relevant_patterns = engine.get_relevant_patterns(
    "SQL injection exploitation",
    limit=3
)
```

## Integração com Componentes Existentes

### 1. Hooks de Aprendizado

```python
# Antes da execução do agente
await learning_hook_before_agent_run(agent, user_input, context)

# Após a execução do agente
await learning_hook_after_agent_run(
    agent=agent,
    user_input=user_input,
    response=response,
    execution_time=execution_time,
    tools_used=tools_used
)

# Início e fim de sessão
learning_hook_session_start(session_id)
results = await learning_hook_session_end()
```

### 2. Modificação do Agent Runner Original

```python
# No agent_runner.py existente, adicionar:
from cai.cli.learning_integration import learning_hook_before_agent_run, learning_hook_after_agent_run

async def run_agent_conversation(self, agent, user_input, parallel_count=1):
    # Hook antes da execução
    context = self._extract_context_from_input(user_input)
    await learning_hook_before_agent_run(agent, user_input, context)

    # Execução normal
    start_time = time.time()
    result = await self._run_single_agent(agent, conversation_input)
    execution_time = time.time() - start_time

    # Hook após a execução
    await learning_hook_after_agent_run(
        agent=agent,
        user_input=user_input,
        response=result,
        execution_time=execution_time,
        tools_used=self._extract_tools_used(result)
    )

    return result
```

## Estratégias de Aprendizado

### 1. Tipos de Padrões

```python
# Exemplos de padrões que o sistema aprende:

# Padrão de Técnica
{
    "type": "technique",
    "description": "Use Nmap with -sV flag for detailed service versioning",
    "confidence_score": 0.89,
    "success_indicators": ["service version identified", "accurate port info"],
    "failure_indicators": ["incomplete scan", "missing service details"]
}

# Padrão de Vulnerabilidade
{
    "type": "vulnerability",
    "description": "WordPress sites often vulnerable to XML-RPC attacks",
    "confidence_score": 0.76,
    "recommendations": ["Check xmlrpc.php endpoint", "Test for pingback abuse"]
}

# Padrão de Exploração
{
    "type": "exploit",
    "description": "Buffer overflow in legacy FTP servers via long USER command",
    "confidence_score": 0.92,
    "success_rate": 0.78
}
```

### 2. Algoritmos de Similaridade

```python
def calculate_pattern_similarity(self, pattern1, pattern2):
    """Calcula similaridade entre padrões usando múltiplas métricas."""

    # Similaridade de descrição (TF-IDF)
    desc_sim = self._text_similarity(pattern1.description, pattern2.description)

    # Similaridade de tipo
    type_sim = 1.0 if pattern1.pattern_type == pattern2.pattern_type else 0.3

    # Similaridade de sucesso
    success_sim = 1.0 - abs(pattern1.success_rate - pattern2.success_rate)

    # Peso combinado
    combined_sim = (desc_sim * 0.6) + (type_sim * 0.3) + (success_sim * 0.1)

    return combined_sim
```

## Monitoramento e Métricas

### 1. Dashboard de Aprendizado

```python
def get_learning_dashboard():
    """Gera dashboard com métricas de aprendizado."""
    engine = get_learning_engine()
    stats = engine.get_learning_stats()

    return {
        "overview": {
            "total_patterns": stats['total_patterns'],
            "active_sessions": stats['active_sessions'],
            "average_confidence": stats['average_confidence'],
            "learning_enabled": get_learning_config().is_enabled()
        },
        "patterns_by_type": stats['pattern_types'],
        "recent_activity": engine.get_recent_patterns(limit=5),
        "performance_metrics": {
            "pattern_discovery_rate": calculate_discovery_rate(),
            "success_rate_trend": get_success_rate_trend(),
            "user_feedback_score": get_average_feedback_rating()
        }
    }
```

### 2. Alertas e Notificações

```python
def check_learning_health():
    """Verifica saúde do sistema de aprendizado."""

    issues = []

    # Verificar se há padrões suficientes
    if engine.get_learning_stats()['total_patterns'] < 10:
        issues.append("Poucos padrões aprendidos - continue usando o sistema")

    # Verificar taxa de sucesso
    if stats['average_confidence'] < 0.5:
        issues.append("Baixa confiança nos padrões - revisar configurações")

    # Verificar espaço em disco
    if get_disk_usage() > 0.9:
        issues.append("Pouco espaço para base de conhecimento")

    return issues
```

## Melhores Práticas

### 1. Configuração Inicial
- Comece com thresholds conservadores (confiança > 0.7)
- Use modelos de qualidade para análise (GPT-4, Claude)
- Configure retenção adequada de dados

### 2. Monitoramento Contínuo
- Monitore métricas de aprendizado regularmente
- Ajuste thresholds baseado em performance
- Faça backup da base de conhecimento

### 3. Privacidade e Segurança
- Configure anonymization para dados sensíveis
- Exclua comandos com credenciais
- Implemente políticas de retenção de dados

### 4. Performance
- Limite análises concorrentes para evitar sobrecarga
- Configure timeouts apropriados
- Use compressão para dados antigos

## Exemplos Práticos

### 1. Cenário de Pentest

```python
# Configuração para pentest
config = get_learning_config()
config.set('learning_config.pattern_similarity_threshold', 0.8)
config.set('learning_config.max_patterns_per_session', 15)

# Executar pentest com aprendizado
runner = EnhancedAgentRunner(console)
runner.enable_learning()

# O sistema aprenderá:
# - Técnicas de reconhecimento eficazes
# - Vetores de ataque bem-sucedidos
# - Respostas a defesas encontradas
# - Padrões de vulnerabilidades por tipo de sistema
```

### 2. Cenário de Bug Bounty

```python
# Configuração para bug bounty
config.update_model_config(
    model_name="openai/gpt-4o",
    temperature=0.2  # Mais conservador para precisão
)

# Foco em padrões de aplicações web
learning_manager.start_session("web_app_bounty_session")

# O sistema aprenderá:
# - Endpoints comumente vulneráveis
# - Técnicas de bypass de WAF
# - Padrões de injeção bem-sucedidos
# - Respostas de aplicações a ataques
```

## Troubleshooting

### Problemas Comuns

**1. Poucos Padrões Sendo Criados**
```python
# Verificar configuração
config = get_learning_config()
print(f"Threshold atual: {config.get_min_confidence_threshold()}")

# Reduzir threshold se necessário
config.set('learning_config.min_confidence_threshold', 0.6)
```

**2. Performance Lenta**
```python
# Otimizar configurações
config.set('performance_config.max_concurrent_analyses', 2)
config.set('learning_config.learning_interval_minutes', 60)
```

**3. Padrões Irrelevantes**
```python
# Ajustar similaridade
config.set('learning_config.pattern_similarity_threshold', 0.9)

# Ou resetar base de conhecimento
engine = get_learning_engine()
engine.clear_irrelevant_patterns()
```

## Conclusão

O sistema de aprendizado contínuo do CAI representa uma evolução significativa na automação de segurança cibernética. Ao aprender com cada interação, o sistema se torna progressivamente mais eficaz, adaptando-se a novos cenários e melhorando sua capacidade de identificar e explorar vulnerabilidades.

A implementação modular permite fácil integração com o código existente, enquanto as configurações flexíveis permitem adaptação a diferentes cenários de uso. O resultado é um framework que não apenas executa tarefas de segurança, mas evolui e melhora continuamente com o uso.
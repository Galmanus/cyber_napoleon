"""
Demonstração Completa do Sistema de Aprendizado Contínuo

Este script demonstra como configurar e usar todas as funcionalidades
do sistema de aprendizado contínuo do CAI.
"""

import asyncio
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table


async def main():
    """Demonstração completa do sistema de aprendizado."""
    console = Console()

    console.print(Panel.fit(
        "[bold blue]🧠 Sistema de Aprendizado Contínuo do CAI[/bold blue]\n"
        "[dim]Demonstração completa das funcionalidades[/dim]",
        border_style="blue"
    ))

    # 1. Configuração Inicial
    console.print("\n[bold green]1. Configuração Inicial[/bold green]")

    try:
        from cai.cli.learning_config import setup_learning_environment, get_learning_config
        from cai.cli.learning_integration import initialize_learning_integration

        # Setup do ambiente
        success = setup_learning_environment()
        if success:
            console.print("✅ Ambiente de aprendizado configurado")

            # Inicializar integração
            await initialize_learning_integration()
            console.print("✅ Sistema de integração inicializado")

        # Mostrar configuração atual
        config = get_learning_config()
        console.print(f"📊 Configuração: {config}")

    except Exception as e:
        console.print(f"❌ Erro na configuração: {e}")
        return

    # 2. Demonstração de Componentes
    console.print("\n[bold green]2. Demonstração de Componentes[/bold green]")

    try:
        from cai.cli.continuous_learning import get_learning_engine
        from cai.cli.learning_integration import get_learning_integration
        from cai.cli.enhanced_agent_runner import EnhancedAgentRunner

        # Obter instâncias dos componentes
        engine = get_learning_engine()
        integration = get_learning_integration()
        runner = EnhancedAgentRunner(console)

        console.print("✅ Componentes inicializados:")
        console.print(f"   • Engine: {len(engine.learning_patterns)} padrões")
        console.print(f"   • Integração: {'habilitada' if integration.learning_enabled else 'desabilitada'}")
        console.print(f"   • Runner: aprendizado {'habilitado' if runner.learning_enabled else 'desabilitado'}")

    except Exception as e:
        console.print(f"❌ Erro nos componentes: {e}")
        return

    # 3. Simulação de Interações de Aprendizado
    console.print("\n[bold green]3. Simulação de Interações[/bold green]")

    # Simular algumas interações de aprendizado
    sample_interactions = [
        {
            'agent_name': 'ReconAgent',
            'user_input': 'Scan the network for open ports',
            'response': 'Found 5 open ports: 22(SSH), 80(HTTP), 443(HTTPS), 3306(MySQL), 5432(PostgreSQL)',
            'success': True,
            'execution_time': 15.2,
            'tools_used': ['nmap', 'masscan']
        },
        {
            'agent_name': 'ExploitAgent',
            'user_input': 'Try to exploit the MySQL service',
            'response': 'Successfully exploited MySQL with CVE-2012-2122 - gained root access',
            'success': True,
            'execution_time': 8.7,
            'tools_used': ['metasploit', 'sqlmap']
        },
        {
            'agent_name': 'ReconAgent',
            'user_input': 'Enumerate users on the compromised system',
            'response': 'Found 15 user accounts, 3 with admin privileges',
            'success': True,
            'execution_time': 12.1,
            'tools_used': ['enum4linux', 'ldapsearch']
        },
        {
            'agent_name': 'PostExploitAgent',
            'user_input': 'Extract sensitive files from the system',
            'response': 'Failed to extract files - permission denied on /etc/shadow',
            'success': False,
            'execution_time': 25.3,
            'tools_used': ['scp', 'tar']
        }
    ]

    # Registrar interações
    integration.start_session("demo_session_001")

    for i, interaction in enumerate(sample_interactions, 1):
        console.print(f"📝 Registrando interação {i}/4...")

        await integration.record_agent_interaction(
            agent_name=interaction['agent_name'],
            user_input=interaction['user_input'],
            agent_response=interaction['response'],
            success=interaction['success'],
            execution_time=interaction['execution_time'],
            tools_used=interaction['tools_used']
        )

    console.print("✅ Interações registradas")

    # 4. Análise de Padrões
    console.print("\n[bold green]4. Análise de Padrões Aprendidos[/bold green]")

    try:
        # Analisar sessão
        patterns = await engine.analyze_session_patterns("demo_session_001")

        if patterns:
            console.print(f"🎯 Descobertos {len(patterns)} novos padrões:")

            table = Table(title="Padrões Aprendidos")
            table.add_column("Tipo", style="cyan")
            table.add_column("Descrição", style="white")
            table.add_column("Confiança", style="green")
            table.add_column("Sucesso", style="yellow")

            for pattern in patterns:
                table.add_row(
                    pattern.pattern_type,
                    pattern.description[:50] + "..." if len(pattern.description) > 50 else pattern.description,
                    ".1f",
                    ".1f"
                )

            console.print(table)
        else:
            console.print("ℹ️  Nenhum padrão novo descoberto nesta sessão")

    except Exception as e:
        console.print(f"❌ Erro na análise: {e}")

    # 5. Consulta de Insights
    console.print("\n[bold green]5. Consulta de Insights[/bold green]")

    try:
        # Obter insights para diferentes contextos
        contexts = [
            "network scanning and reconnaissance",
            "database exploitation techniques",
            "privilege escalation methods"
        ]

        for context in contexts:
            insights = await integration.get_learning_insights(context)

            if insights['insights']:
                console.print(f"\n💡 Insights para '{context}':")
                for insight in insights['insights'][:2]:  # Mostrar top 2
                    console.print(f"   • {insight['description']}")
                    console.print(".1f"            else:
                console.print(f"   ℹ️  Nenhum insight específico para '{context}'")

    except Exception as e:
        console.print(f"❌ Erro na consulta: {e}")

    # 6. Estatísticas do Sistema
    console.print("\n[bold green]6. Estatísticas do Sistema[/bold green]")

    try:
        stats = engine.get_learning_stats()
        status = integration.get_learning_status()

        console.print("📈 Estatísticas atuais:")
        console.print(f"   • Padrões totais: {stats['total_patterns']}")
        console.print(f"   • Confiança média: {stats['average_confidence']:.2f}")
        console.print(f"   • Taxa de sucesso média: {stats['average_success_rate']:.2f}")
        console.print(f"   • Sessões ativas: {stats['active_sessions']}")
        console.print(f"   • Sistema habilitado: {status['enabled']}")

        if stats['pattern_types']:
            console.print("   • Padrões por tipo:")
            for ptype, count in stats['pattern_types'].items():
                console.print(f"     - {ptype}: {count}")

    except Exception as e:
        console.print(f"❌ Erro nas estatísticas: {e}")

    # 7. Demonstração de Feedback
    console.print("\n[bold green]7. Demonstração de Feedback[/bold green]")

    try:
        # Adicionar feedback do usuário
        feedback_examples = [
            ("The reconnaissance was very thorough", 5),
            ("Exploit technique worked perfectly", 5),
            ("User enumeration could be faster", 3)
        ]

        for feedback, rating in feedback_examples:
            integration.add_user_feedback(feedback, rating)
            console.print(f"📝 Feedback registrado: '{feedback}' (⭐ {rating}/5)")

        console.print("✅ Feedback registrado com sucesso")

    except Exception as e:
        console.print(f"❌ Erro no feedback: {e}")

    # 8. Finalização da Sessão
    console.print("\n[bold green]8. Finalização da Sessão[/bold green]")

    try:
        # Finalizar sessão e obter resultados
        results = await integration.end_session_and_learn()

        console.print("🏁 Sessão finalizada:")
        console.print(f"   • Sessão ID: {results['session_id']}")
        console.print(f"   • Padrões descobertos: {results['patterns_discovered']}")
        console.print(f"   • Total de padrões: {results['total_patterns']}")
        console.print(f"   • Novos padrões: {len(results['new_patterns'])}")

        if results['new_patterns']:
            console.print("   • Novos padrões aprendidos:")
            for pattern in results['new_patterns'][:3]:  # Mostrar top 3
                console.print(f"     - {pattern['type']}: {pattern['description'][:40]}...")

    except Exception as e:
        console.print(f"❌ Erro na finalização: {e}")

    # 9. Resumo Final
    console.print("\n[bold green]9. Resumo da Demonstração[/bold green]")

    final_stats = engine.get_learning_stats()

    summary_panel = Panel(
        f"[bold]Demonstração Concluída![/bold]\n\n"
        f"📊 [cyan]Padrões Totais:[/cyan] {final_stats['total_patterns']}\n"
        f"🎯 [cyan]Confiança Média:[/cyan] {final_stats['average_confidence']:.2f}\n"
        f"✅ [cyan]Taxa de Sucesso:[/cyan] {final_stats['average_success_rate']:.2f}\n"
        f"🔄 [cyan]Sessões Ativas:[/cyan] {final_stats['active_sessions']}\n\n"
        f"[dim]O sistema de aprendizado contínuo está funcionando corretamente "
        f"e aprendendo com cada interação![/dim]",
        title="[bold blue]🎉 Resultado Final[/bold blue]",
        border_style="green"
    )

    console.print(summary_panel)

    # 10. Próximos Passos
    console.print("\n[bold yellow]💡 Próximos Passos Recomendados:[/bold yellow]")
    console.print("   1. Configure o modelo de aprendizado em learning_config.py")
    console.print("   2. Ajuste os thresholds de confiança conforme necessário")
    console.print("   3. Integre com seus agentes existentes usando EnhancedAgentRunner")
    console.print("   4. Monitore o aprendizado através das estatísticas")
    console.print("   5. Adicione feedback regular para melhorar os padrões")

    console.print("\n[dim]Para mais informações, consulte learning_guide.md[/dim]")


if __name__ == "__main__":
    # Verificar se estamos em um ambiente adequado
    if not os.path.exists("src/cai/cli"):
        print("Erro: Execute este script do diretório raiz do projeto CAI")
        exit(1)

    # Executar demonstração
    asyncio.run(main())
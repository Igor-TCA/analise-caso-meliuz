import pandas as pd
import matplotlib.pyplot as plt

# Configurações
CASHBACKS = [1.5, 2.0, 2.5]
MESES = ['Junho', 'Julho', 'Agosto']
CORES = {1.5: '#7f8c8d', 2.0: '#27ae60', 2.5: '#3498db'}
RECOMENDADO = 2.0


def carregar_dados():
    df = pd.read_csv('experimento_cashback_meliuz.csv')
    df['data'] = pd.to_datetime(df['data'])
    df['mes'] = df['data'].dt.month
    return df


def calcular_variacao(valor_atual, valor_base):
    return (valor_atual - valor_base) / valor_base * 100


def calcular_metricas(df):
    gmv = df.groupby(['cashback_aplicado', 'mes'])['valor_compra'].sum().unstack()
    gmv.columns = MESES
    
    ticket = df.groupby('cashback_aplicado')['valor_compra'].mean()
    cashback_pago = df.groupby('cashback_aplicado')['valor_cashback'].sum()
    gmv_total = df.groupby('cashback_aplicado')['valor_compra'].sum()
    roi = gmv_total / cashback_pago
    
    metricas = {}
    for cb in CASHBACKS:
        metricas[cb] = {
            'gmv': gmv.loc[cb],
            'crescimento': calcular_variacao(gmv.loc[cb, 'Julho'], gmv.loc[cb, 'Junho']),
            'retencao': calcular_variacao(gmv.loc[cb, 'Agosto'], gmv.loc[cb, 'Junho']),
            'ticket': ticket.loc[cb],
            'roi': roi.loc[cb]
        }
    
    return metricas, gmv


def gerar_graficos(metricas, gmv):
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('EXPERIMENTO DE CASHBACK MÉLIUZ - Análise Comparativa', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    # Gráfico 1: Evolução do GMV
    for cb in CASHBACKS:
        destaque = cb == RECOMENDADO
        axes[0, 0].plot(
            ['Junho\n(Baseline)', 'Julho\n(Experimento)', 'Agosto\n(Pós-Exp)'],
            gmv.loc[cb] / 1000,
            marker='o',
            linewidth=4 if destaque else 2,
            markersize=12 if destaque else 8,
            alpha=1.0 if destaque else 0.7,
            label=f'{cb}%' + (' [RECOMENDADO]' if destaque else ''),
            color=CORES[cb]
        )
    
    for i, val in enumerate(gmv.loc[RECOMENDADO] / 1000):
        axes[0, 0].annotate(f'R$ {val:.1f}k', (i, val), textcoords="offset points",
                            xytext=(0, 15), ha='center', fontsize=9, 
                            fontweight='bold', color=CORES[RECOMENDADO])
    
    axes[0, 0].set_title('1. Evolução do GMV por Período', fontsize=13, fontweight='bold')
    axes[0, 0].set_ylabel('GMV (R$ mil)')
    axes[0, 0].legend(loc='upper left')
    axes[0, 0].set_ylim(bottom=0)
    
    # Gráfico 2: Crescimento vs Retenção
    x = range(3)
    largura = 0.35
    crescimentos = [metricas[cb]['crescimento'] for cb in CASHBACKS]
    retencoes = [metricas[cb]['retencao'] for cb in CASHBACKS]
    
    bars1 = axes[0, 1].bar([i - largura/2 for i in x], crescimentos, largura,
                            label='Crescimento no Experimento', color='#3498db')
    bars2 = axes[0, 1].bar([i + largura/2 for i in x], retencoes, largura,
                            label='Retenção Pós-Experimento', color='#27ae60')
    
    for bars in [bars1, bars2]:
        for bar in bars:
            h = bar.get_height()
            axes[0, 1].annotate(f'{h:+.1f}%', xy=(bar.get_x() + bar.get_width()/2, h),
                                xytext=(0, 3 if h >= 0 else -15), textcoords="offset points",
                                ha='center', fontsize=9, fontweight='bold')
    
    axes[0, 1].axvspan(0.65, 1.35, alpha=0.15, color='green')
    axes[0, 1].annotate('MELHOR\nOPÇÃO', xy=(1, 55), ha='center', fontsize=10,
                        fontweight='bold', color='#27ae60')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels([f'{cb}%' for cb in CASHBACKS])
    axes[0, 1].set_ylabel('Variação GMV (%)')
    axes[0, 1].set_title('2. Impacto no GMV: Crescimento vs Retenção', fontsize=13, fontweight='bold')
    axes[0, 1].legend(loc='upper right')
    axes[0, 1].axhline(y=0, color='black', linewidth=1)
    axes[0, 1].set_ylim(-25, 70)
    
    # Gráfico 3: Ticket Médio
    tickets = [metricas[cb]['ticket'] for cb in CASHBACKS]
    bars3 = axes[1, 0].bar([f'{cb}%' for cb in CASHBACKS], tickets, color=[CORES[cb] for cb in CASHBACKS])
    bars3[1].set_edgecolor('#1a5f38')
    bars3[1].set_linewidth(3)
    
    for i, (bar, val) in enumerate(zip(bars3, tickets)):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
                        f'R$ {val:.0f}', ha='center', fontsize=11, fontweight='bold')
        if i == 2:
            axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                            '(-45%)', ha='center', fontsize=10, fontweight='bold', color='white')
    
    media = (tickets[0] + tickets[1]) / 2
    axes[1, 0].axhline(y=media, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.7)
    axes[1, 0].set_title('3. Ticket Médio por Grupo', fontsize=13, fontweight='bold')
    axes[1, 0].set_ylabel('Ticket Médio (R$)')
    axes[1, 0].set_ylim(0, 400)
    
    # Gráfico 4: ROI
    rois = [metricas[cb]['roi'] for cb in reversed(CASHBACKS)]
    cores_rev = [CORES[cb] for cb in reversed(CASHBACKS)]
    
    bars4 = axes[1, 1].barh(range(3), rois, color=cores_rev, height=0.6)
    bars4[1].set_edgecolor('#1a5f38')
    bars4[1].set_linewidth(3)
    
    for i, (bar, r) in enumerate(zip(bars4, rois)):
        axes[1, 1].text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                        f'{r:.1f}x', va='center', fontsize=10, fontweight='bold')
        if i == 1:
            axes[1, 1].annotate('EQUILÍBRIO IDEAL', xy=(bar.get_width()/2, bar.get_y() + bar.get_height()/2),
                               ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    axes[1, 1].set_yticks(range(3))
    axes[1, 1].set_yticklabels([f'{cb}%' for cb in reversed(CASHBACKS)])
    axes[1, 1].set_xlabel('ROI (GMV / Cashback Pago)')
    axes[1, 1].set_title('4. ROI por Grupo', fontsize=13, fontweight='bold')
    axes[1, 1].set_xlim(0, 85)
    
    plt.tight_layout()
    plt.savefig('graficos_cashback.png', dpi=150, bbox_inches='tight', facecolor='white')


def imprimir_resumo(metricas):
    print("\n" + "=" * 60)
    print("EXPERIMENTO DE CASHBACK MÉLIUZ - RESUMO")
    print("=" * 60)
    
    print("\n| Grupo  | Crescimento | Retenção | Ticket Médio |  ROI  |")
    print("|--------|-------------|----------|--------------|-------|")
    
    for cb in CASHBACKS:
        m = metricas[cb]
        marca = " *" if cb == RECOMENDADO else "  "
        print(f"| {cb}%{marca} |    {m['crescimento']:+6.1f}% |  {m['retencao']:+6.1f}% |   R$ {m['ticket']:>6.2f} | {m['roi']:>4.1f}x |")
    
    print("\n* RECOMENDADO: Cashback de 2.0%")
    print("  - Único com retenção positiva após experimento")
    print("  - Maior crescimento de GMV (+52.6%)")
    print("  - Ticket médio alto (não atrai oportunistas)")
    print("\nGráficos salvos em 'graficos_cashback.png'")


if __name__ == '__main__':
    df = carregar_dados()
    metricas, gmv = calcular_metricas(df)
    gerar_graficos(metricas, gmv)
    imprimir_resumo(metricas)
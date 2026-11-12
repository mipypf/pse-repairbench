# ベンチマーク設計

## 研究スコープ

PSE-RepairBench v0.1 は、LLM が故障ケースの観測情報だけを使って、
実行可能な DWSIM プロセスシミュレーションを診断・修復できるかを
評価する。

初期論文のスコープは意図的に狭くする。

- シミュレータ: DWSIM のみ。
- タスク設定: faulty-only の one-shot repair。
- インターフェース: JSON 観測パッケージを入力し、JSON repair action
  を出力する。
- 修復対象: モデルに `.dwxmz` や `.dwxml` を直接編集させず、executor
  が適用できる構造化 action とする。
- 評価優先度: executable target success を主指標、gold action への近さを
  副指標とする。

reference-assisted repair、シミュレータ feedback を使う agentic retry、
IDAES 対応、multi-simulator claim は将来課題とする。これらは v0.1 の
ベンチマーク契約には含めない。

## 中心問い

LLM は、単なる topology や syntax の修正ではなく、プロセス工学的な
文脈を使って、実行可能な化学プロセス flowsheet を修復できるか。

主分析では、one-shot repair の性能が fault class と observation condition
によってどう変わるかを示す。

## インスタンス契約

各インスタンスは、厳密な public/hidden 分離を持つ制御された修復問題で
ある。

Repository layout は [repository_layout.md](repository_layout.md) に従い、
各 case は `instances/seed/<instance_id>/instance.json` または
`instances/legacy/<instance_id>/instance.json` を正本とする。

public artifacts はモデルに見せる。

- faulty flowsheet
- topology observation
- parameter observation
- simulator log
- stream table
- task statement と LLM input packet

hidden artifacts は生成と評価にのみ使う。

- base flowsheet
- injected-fault metadata
- gold repair action
- repair semantics label
- base/faulty/repaired run artifacts
- metrics report

base flowsheet と injected-fault metadata は、明示的に許可された public task
metadata、例えば target success criteria を除き、public observations の生成に
使ってはならない。

## Repair Action 契約

モデルは、少数で安定した canonical repair action を出力する。新しい
ベンチマークケースを追加するときは、専用 action type を増やすのではなく、
既存 action type の中に parameter name を追加することを優先する。

初期 canonical action type:

- `set_unit_parameter`

Future canonical action families should be added only after executor/evaluator support exists:

- `set_stream_condition`
- `set_property_model`
- `connect_stream`
- `disconnect_stream`
- `set_solver_option`

例:

```json
{
  "diagnosis": "The product stream misses the oxygen purity target because the column reflux ratio is too low.",
  "repair_actions": [
    {
      "type": "set_unit_parameter",
      "target": {
        "kind": "unit_operation",
        "guid": "DC-84eedf9c-acf3-4dfc-8675-2245dc73de75",
        "tag": "DC-01"
      },
      "parameter": {
        "namespace": "column_specification",
        "name": "reflux_ratio"
      },
      "value": 7.502,
      "unit": null,
      "rationale": "Increasing reflux restores separation performance."
    }
  ]
}
```

`restore_reflux_ratio` や `move_feed_stage_to_gold` のような専門的ラベルは、
分析用の hidden metadata に置く。canonical contract が明らかに不足しない限り、
これらをモデル向け action type にしない。

## Fault Class

各インスタンスは、主要な reasoning class を1つ持つ。

- `T_topology`: 接続、欠損 object、構造的な誤り。
- `P_parameter`: unit、stream、solver parameter の誤り。
- `M_model`: 不適切な thermodynamic model や property model の選択。
- `C_convergence`: recycle、初期値、tear、solver convergence の問題。
- `E_performance`: simulation は走るが、purity、recovery、conversion、duty、
  pressure、plausibility target を満たさない問題。

この分類により、topology repair と process-engineering repair を分けて扱う。

## Observation Condition

v0.1 は one-shot 設定である。モデルは faulty-case observation package を
1つ受け取り、1つの repair JSON を返す。

初期 observation condition:

1. Topology only.
2. Topology + parameters.
3. Topology + simulator log.
4. Topology + stream table.
5. Topology + parameters + log + stream table.

agentic retry は v0.1 から除外する。tool-use や探索戦略を混ぜる前に、まず
モデル間の one-shot 性能差を測るためである。

## Leakage Policy

public artifacts は、固定された leakage policy を持つ rule-based pipeline で
生成する。

- Topology observations は object identity、type、port、connectivity を含んで
  よいが、parameter value や calculated stream result を含めてはならない。
- Parameter observations は faulty-case の configured value を含んでよいが、
  base value、gold value、injected-fault label、simulator feedback を含めては
  ならない。
- Simulator logs からは local path、benchmark metadata、hidden repair を直接
  名指しする text を除去する。
- Stream tables は faulty-case の calculated value と finite/NaN status を含んで
  よいが、base-run value を含めてはならない。
- Public task text は、それが repair task の一部である場合に限り target
  criteria を記述してよい。
- Release validation は、明示的に許可された field 以外に hidden path、base-flow
  value、exact gold value、injected-fault label が現れた場合に失敗させる。
- feed stage などの小さな整数 gold value は、public topology や parameter
  context に自然に現れやすいため、raw token としては leakage 判定しない。
  代わりに direct-repair text、hidden label、mock/metrics path、legacy
  specialized action 名の露出を release validation で失敗させる。

release instance では hidden-to-public leakage をゼロにすることを目標とする。

## 評価

主指標は executable target success とする。

- repaired flowsheet が load できる。
- DWSIM が fatal error なしで実行できる。
- convergence が必要な場合、simulation が収束する。
- repaired result が instance success criteria を満たす。

Gold action match は副次的な診断指標とする。将来の学習データとして重要だが、
executable success より優先しない。

Gold proximity は分解して測る。

- target object match
- parameter または connection match
- numeric change の direction match
- numeric repair の value closeness
- repair minimality
- diagnosis または reasoning-class match

成功した repair は次のように分類できる。

- `gold_equivalent`: gold repair と同じ intervention。
- `near_gold`: target と parameter は同じだが、値が近似。
- `alternate_valid`: gold とは異なる intervention だが、全 criteria を満たす。
- `over_repair`: 成功しているが、無関係または過剰な変更を含む。
- `failed_repair`: executable target success を満たさない。

## Seed Plan

次の milestone は、同じ contract を process category 横断で検証する
3-instance seed set である。

| Category | Purpose |
| --- | --- |
| Flash/separator | topology、stream、単純な unit-parameter repair を検証する。 |
| Distillation | column specification と performance repair を検証する。 |
| Reaction-recycle | one-shot 形式で recycle/convergence-oriented repair を検証する。 |

現在の状態:

- `distillation_002_reflux_ratio_single` が release-supported reflux-ratio
  vertical slice である。
- `distillation_002_feed_stage_single` が release-supported feed-stage vertical
  slice である。
- `distillation_001_feed_stage_single` は legacy placeholder であり、
  release-quality instance ではない。

canonical action contract、厳密な leakage check、executable rerun、安定した
evaluator output を備えた seed set が release validation を通過してから、
データセットを拡張する。

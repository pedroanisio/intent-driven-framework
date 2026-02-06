import Lake
open Lake DSL

package «intent-framework» where
  leanOptions := #[
    ⟨`autoImplicit, true⟩
  ]

@[default_target]
lean_lib IntentDrivenFramework where
  srcDir := "."

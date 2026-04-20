import React from 'react';
import { T } from '../tokens';
import { Label, Serif, Mono } from './primitives';
import { useIsMobile } from '../hooks/useIsMobile';

interface Props {
  eyebrow: string;
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
}

export function PageHeader({ eyebrow, title, subtitle, right }: Props) {
  const mobile = useIsMobile();
  return (
    <div style={{
      padding: mobile ? '20px 20px 14px' : '28px 40px 22px',
      borderBottom: `1px solid ${T.hairline}`,
      display: 'flex',
      flexDirection: mobile ? 'column' : 'row',
      alignItems: mobile ? 'stretch' : 'flex-end',
      justifyContent: 'space-between',
      gap: mobile ? 14 : 24,
      background: T.paper,
      flexShrink: 0,
    }}>
      <div>
        <Label>{eyebrow}</Label>
        <div style={{ marginTop: 6, display: 'flex', alignItems: 'baseline', gap: 14, flexWrap: 'wrap' }}>
          <Serif size={mobile ? 44 : 56} italic>{title}</Serif>
          {subtitle && <Mono size={11} color={T.ink3}>{subtitle}</Mono>}
        </div>
      </div>
      {right && (
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>{right}</div>
      )}
    </div>
  );
}

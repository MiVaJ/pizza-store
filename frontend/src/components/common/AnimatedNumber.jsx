import React, { useEffect, useRef } from 'react';
import NumberFlow from '@number-flow/react';

export default function AnimatedNumber({ value }) {
  // Карман памяти, чтобы помнить, какая цена была до этого клика
  const prevValueRef = useRef(value);

  useEffect(() => {
    // Перезаписываем цену в кармане при каждом изменении стоимости
    prevValueRef.current = value;
  }, [value]);

  // Проверяем была ли прошлая стоимость 0
  const isFirstRender = prevValueRef.current === 0;

  return (
    <div className="flex h-6 w-20 items-center justify-center overflow-hidden select-none">
      <NumberFlow
        value={value}
        // animated={!isFirstRender} — отключает горизонтальное плавание нуля при первом вылете.
        animated={!isFirstRender}
        springs={{
          layout: { type: 'spring', stiffness: 140, damping: 16, mass: 0.5 },
        }}
        className="text-base font-black text-white leading-6 tracking-tight tabular-nums"
      />
      <span className="ml-1 text-base font-black text-white leading-6">₽</span>
    </div>
  );
}

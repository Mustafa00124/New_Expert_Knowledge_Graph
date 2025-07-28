import { Box, TextLink } from '@neo4j-ndl/react';

const ImporterInput = () => {
  return (
    <Box className='py-2'>
              <TextLink isExternalLink={true} href='https://example.com/import/models' target='_blank'>
        Aura Data Models
      </TextLink>
    </Box>
  );
};
export default ImporterInput;
